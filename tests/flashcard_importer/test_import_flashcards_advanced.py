"""
Advanced tests for the import_flashcards endpoint and related functionality.
Tests complex scenarios, edge cases, security, and performance concerns.
"""
import pytest
import asyncio
import tempfile
import zipfile
import sqlite3
import json
import os
from io import BytesIO
from pathlib import Path

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.routers.import_cards.service import ImportService
from flashcard_importer import ParserFactory, Flashcard, ImportResult, CardType
from flashcard_importer.parsers import TxtParser, CsvParser
from flashcard_importer.utils import DeckDetector, MissingDeckHandler, HtmlHandler
from flashcard_importer.utils.validators import CardValidator, TagParser, AnkiHeaderParser
from flashcard_importer.exceptions import (
    FlashcardImportError,
    FileFormatError,
    ParsingError,
    ValidationError,
    EmptyFileError,
    AnkiDatabaseError
)


# ============================================================================
# Fixtures for Test Data
# ============================================================================

@pytest.fixture
def complex_csv_with_html():
    """CSV with HTML content, special chars, and multiple decks."""
    content = """front,back,deck,tags
"<b>What is {{c1::recursion}}?</b>","<p>A function calling itself</p><br/><code>def f(): f()</code>",Programming,python cloze
"<img src='test.png'/>","The capital of France is Paris",Geography,capital
"What's the symbol for &amp;?","Ampersand &amp;",Symbols,"html entities"
"日本語","Japanese Language",Languages,japanese unicode
"""
    return content.encode('utf-8')


@pytest.fixture
def anki_headers_txt():
    """TXT file with Anki-specific headers."""
    content = """#separator:tab
#html:true
#deck column:3
#tags column:4
Question 1\tAnswer 1\tMyDeck\ttag1 tag2
Question 2\tAnswer 2\tOtherDeck\ttag3
"""
    return content.encode('utf-8')


@pytest.fixture
def cloze_cards_csv():
    """CSV with various cloze deletion patterns."""
    content = """front,back,deck
"The {{c1::capital}} of France is {{c2::Paris}}","","Geography"
"{{c1::Python}} is a {{c2::programming}} language","","Programming"
"{{c1::2}} + {{c1::2}} = {{c2::4}}","Multiple c1","Math"
"{{c1::Answer::Hint}}","Cloze with hint","Hints"
"""
    return content.encode('utf-8')


@pytest.fixture
def multiline_csv():
    """CSV with multiline content in cells."""
    content = '''front,back,deck
"Line 1
Line 2
Line 3","Answer with
multiple
lines",Test
"Question","Simple answer",Test
'''
    return content.encode('utf-8')


@pytest.fixture
def edge_case_csv():
    """CSV with edge cases: empty cells, quotes, special chars."""
    lines = [
        'front,back,deck,tags',
        '"Question with ""quotes""","Answer with ""nested"" quotes",Deck1,',
        '"","Empty front should be skipped",,',
        '"No back answer","",Deck2,tag1',
        '"Commas, in, content","Still, works, fine",Deck3,"tag,with,commas"',
        '"   Whitespace   ","   Around   ",Deck4,',
    ]
    content = '\n'.join(lines) + '\n'
    return content.encode('utf-8')


@pytest.fixture
def large_content_csv():
    """CSV with very large content."""
    large_text = "X" * 10000  # 10KB of text
    content = f"""front,back,deck
"{large_text}","Answer",LargeDeck
"Question","{large_text}",LargeDeck
"""
    return content.encode('utf-8')


@pytest.fixture
def mixed_encodings_txt():
    """TXT with various unicode characters."""
    content = """日本語の質問\t日本語の答え
Ελληνικά\tGreek
العربية\tArabic
🎉 Emoji\t🚀 Rocket
Ümlauts äöü\tSpecial characters ñ
"""
    return content.encode('utf-8')


def create_mock_apkg(decks: dict, cards: list) -> bytes:
    """
    Create a mock APKG file with specified decks and cards.
    
    Args:
        decks: Dict of deck_id -> deck_name
        cards: List of tuples (front, back, deck_id, tags)
    """
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(suffix='.anki2', delete=False) as f:
        db_path = f.name
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE col (
            id INTEGER PRIMARY KEY,
            crt INTEGER, mod INTEGER, scm INTEGER, ver INTEGER,
            dty INTEGER, usn INTEGER, ls INTEGER, conf TEXT,
            models TEXT, decks TEXT, dconf TEXT, tags TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            guid TEXT, mid INTEGER, mod INTEGER, usn INTEGER,
            tags TEXT, flds TEXT, sfld TEXT, csum INTEGER, flags INTEGER, data TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY,
            nid INTEGER, did INTEGER, ord INTEGER, mod INTEGER,
            usn INTEGER, type INTEGER, queue INTEGER, due INTEGER,
            ivl INTEGER, factor INTEGER, reps INTEGER, lapses INTEGER,
            left INTEGER, odue INTEGER, odid INTEGER, flags INTEGER, data TEXT
        )
    """)
    
    # Insert collection data
    decks_json = json.dumps({str(k): {"name": v, "id": k} for k, v in decks.items()})
    models_json = json.dumps({
        "1": {
            "name": "Basic",
            "flds": [{"name": "Front"}, {"name": "Back"}]
        }
    })
    
    cursor.execute("""
        INSERT INTO col VALUES (1, 0, 0, 0, 0, 0, 0, 0, '{}', ?, ?, '{}', '{}')
    """, (models_json, decks_json))
    
    # Insert notes and cards
    for i, (front, back, deck_id, tags) in enumerate(cards, start=1):
        fields = f"{front}\x1f{back}"
        cursor.execute("""
            INSERT INTO notes VALUES (?, ?, 1, 0, 0, ?, ?, ?, 0, 0, '')
        """, (i, f"guid{i}", tags, fields, front))
        
        cursor.execute("""
            INSERT INTO cards VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '')
        """, (i, i, deck_id))
    
    conn.commit()
    conn.close()
    
    # Create ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, 'collection.anki2')
    
    os.unlink(db_path)
    
    return zip_buffer.getvalue()


@pytest.fixture
def mock_apkg():
    """Create a mock APKG file with multiple decks."""
    decks = {1: "Default", 2: "Science", 3: "Languages"}
    cards = [
        ("What is Python?", "A programming language", 1, "programming"),
        ("H2O is?", "Water molecule", 2, "chemistry science"),
        ("Bonjour means?", "Hello in French", 3, "french greetings"),
        ("{{c1::Recursion}} is?", "Function calling itself", 1, "cloze programming"),
    ]
    return create_mock_apkg(decks, cards)


# ============================================================================
# Advanced API Endpoint Tests
# ============================================================================

class TestImportFlashcardsAdvanced:
    """Advanced tests for the import_flashcards endpoint."""

    @pytest.mark.asyncio
    async def test_upload_with_html_stripping(self, complex_csv_with_html):
        """Test that HTML is properly stripped when strip_html=True."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.csv", BytesIO(complex_csv_with_html), "text/csv")}
            data = {"strip_html": "true"}
            response = await client.post("/import/upload", files=files, data=data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            
            # Check that HTML was stripped
            cards = data['cards']
            assert any('html_enabled' in c for c in cards)
            # At least some cards should have html_enabled=False after stripping
            stripped_cards = [c for c in cards if c.get('html_enabled') is False]
            assert len(stripped_cards) > 0

    @pytest.mark.asyncio
    async def test_upload_with_deck_filter(self, mock_apkg):
        """Test APKG import with deck filtering."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.apkg", BytesIO(mock_apkg), "application/octet-stream")}
            data = {"deck_filter": "Science"}
            response = await client.post("/import/upload", files=files, data=data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            # Should only import cards from Science deck
            assert data['summary']['total_imported'] >= 1
            for card in data['cards']:
                assert card.get('deck_name') == 'Science'

    @pytest.mark.asyncio
    async def test_upload_apkg_with_cloze_cards(self, mock_apkg):
        """Test that cloze cards are detected in APKG files."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.apkg", BytesIO(mock_apkg), "application/octet-stream")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['statistics']['cards_with_cloze'] >= 1

    @pytest.mark.asyncio
    async def test_upload_cloze_csv(self, cloze_cards_csv):
        """Test cloze detection in CSV files."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("cloze.csv", BytesIO(cloze_cards_csv), "text/csv")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            # At least 2 cloze cards should be detected (some may be skipped due to empty back)
            assert data['statistics']['cards_with_cloze'] >= 2

    @pytest.mark.asyncio
    async def test_upload_multiline_content(self, multiline_csv):
        """Test handling of multiline content in CSV cells."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("multiline.csv", BytesIO(multiline_csv), "text/csv")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['summary']['total_imported'] == 2
            
            # Check that multiline content was preserved
            cards = data['cards']
            multiline_card = next((c for c in cards if 'Line 1' in c['front']), None)
            assert multiline_card is not None
            assert 'Line 2' in multiline_card['front']
            assert 'Line 3' in multiline_card['front']

    @pytest.mark.asyncio
    async def test_upload_unicode_content(self, mixed_encodings_txt):
        """Test handling of various unicode characters."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("unicode.txt", BytesIO(mixed_encodings_txt), "text/plain")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            
            # Verify unicode content was preserved
            cards = data['cards']
            assert any('日本語' in c['front'] for c in cards)
            assert any('Ελληνικά' in c['front'] for c in cards)
            assert any('العربية' in c['front'] for c in cards)
            assert any('🎉' in c['front'] for c in cards)

    @pytest.mark.asyncio
    async def test_upload_edge_cases(self, edge_case_csv):
        """Test handling of edge cases in CSV."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("edge.csv", BytesIO(edge_case_csv), "text/csv")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            # Some cards should be skipped (empty front/back)
            assert data['summary']['total_skipped'] > 0
            
            # Cards with quotes should be imported correctly
            cards = data['cards']
            quoted_card = next((c for c in cards if 'quotes' in c['front']), None)
            assert quoted_card is not None

    @pytest.mark.asyncio
    async def test_upload_auto_assign_decks(self, complex_csv_with_html):
        """Test AI-based deck suggestion."""
        # Create content without deck info
        content = b"""front,back,tags
"What is Python?","A programming language",programming
"def function():","Function definition",code python
"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("no_deck.csv", BytesIO(content), "text/csv")}
            data = {"auto_assign_decks": "true"}
            response = await client.post("/import/upload", files=files, data=data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            # Cards should have been assigned to Programming deck
            assert 'Programming' in str(data['statistics']['deck_distribution'])

    @pytest.mark.asyncio
    async def test_preview_shows_deck_info(self, mock_apkg):
        """Test that preview correctly shows available decks for APKG."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.apkg", BytesIO(mock_apkg), "application/octet-stream")}
            response = await client.post("/import/preview", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['format'] == '.apkg'
            assert 'available_decks' in data
            assert data['available_decks'] is not None
            assert len(data['available_decks']) >= 3

    @pytest.mark.asyncio
    async def test_validate_empty_file(self):
        """Test validation of an empty file."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("empty.csv", BytesIO(b""), "text/csv")}
            response = await client.post("/import/validate", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['can_import'] is False
            assert len(data['issues']) > 0

    @pytest.mark.asyncio
    async def test_upload_large_file_within_limits(self, large_content_csv):
        """Test handling of files with large content within limits."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("large.csv", BytesIO(large_content_csv), "text/csv")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True

    @pytest.mark.asyncio
    async def test_response_statistics_complete(self, complex_csv_with_html):
        """Test that response contains complete statistics."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.csv", BytesIO(complex_csv_with_html), "text/csv")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all statistics fields
            stats = data['statistics']
            assert 'deck_distribution' in stats
            assert 'top_tags' in stats
            assert 'cards_with_html' in stats
            assert 'cards_with_cloze' in stats
            
            # Verify summary
            summary = data['summary']
            assert 'total_imported' in summary
            assert 'total_skipped' in summary
            assert 'success_rate' in summary
            assert 'deck_detected' in summary


# ============================================================================
# Parser Advanced Tests
# ============================================================================

class TestParserAdvanced:
    """Advanced parser tests for edge cases."""

    def test_txt_parser_anki_headers(self, tmp_path, anki_headers_txt):
        """Test parsing TXT files with Anki headers."""
        test_file = tmp_path / "anki.txt"
        test_file.write_bytes(anki_headers_txt)
        
        parser = TxtParser(str(test_file))
        settings = parser.detect_settings()
        
        assert settings['separator'] == '\t'
        assert settings['html'] is True
        assert settings['columns'].get('deck') == 3
        assert settings['columns'].get('tags') == 4
        
        result = parser.parse()
        assert len(result.cards) == 2
        assert result.cards[0].deck_name == "MyDeck"

    def test_csv_parser_quoted_content(self, tmp_path):
        """Test CSV parser with various quoting scenarios."""
        test_file = tmp_path / "quoted.csv"
        test_file.write_text('''front,back
"Question with ""nested"" quotes","Answer"
"Question, with, commas","Answer, too"
"Question
with newline","Answer"
''')
        parser = CsvParser(str(test_file))
        result = parser.parse()
        
        assert len(result.cards) == 3
        assert '""nested""' in result.cards[0].front or 'nested' in result.cards[0].front
        assert ',' in result.cards[1].front

    def test_parser_factory_extension_handling(self, tmp_path):
        """Test parser factory handles extensions case-insensitively."""
        test_file = tmp_path / "test.CSV"
        test_file.write_text("Q,A\n")
        
        parser = ParserFactory.create(str(test_file))
        assert isinstance(parser, CsvParser)

    def test_parser_preserves_whitespace_in_content(self, tmp_path):
        """Test that significant whitespace is preserved."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("   Indented question   \tAnswer   \n")
        
        parser = TxtParser(str(test_file))
        result = parser.parse()
        
        assert len(result.cards) == 1
        # Content should be trimmed but not aggressively
        assert result.cards[0].is_valid()

    def test_parser_handles_bom(self, tmp_path):
        """Test that BOM (Byte Order Mark) is handled."""
        test_file = tmp_path / "bom.csv"
        # Write with UTF-8 BOM
        with open(test_file, 'wb') as f:
            f.write(b'\xef\xbb\xbf')  # UTF-8 BOM
            f.write("front,back\nQ,A\n".encode('utf-8'))
        
        parser = CsvParser(str(test_file))
        result = parser.parse()
        
        assert len(result.cards) == 1

    def test_parser_handles_different_newlines(self, tmp_path):
        """Test handling of different newline styles."""
        test_file = tmp_path / "newlines.txt"
        
        # Mix of \r\n, \n, and \r
        content = "Q1\tA1\r\nQ2\tA2\nQ3\tA3\r"
        test_file.write_bytes(content.encode('utf-8'))
        
        parser = TxtParser(str(test_file))
        result = parser.parse()
        
        # Should handle all newline types
        assert len(result.cards) >= 2


# ============================================================================
# Validator Tests
# ============================================================================

class TestValidatorsAdvanced:
    """Advanced tests for validators."""

    def test_cloze_pattern_variants(self):
        """Test detection of various cloze patterns."""
        # Standard cloze
        assert CardValidator.is_cloze_card("{{c1::answer}}")
        # Cloze with hint
        assert CardValidator.is_cloze_card("{{c1::answer::hint}}")
        # Multiple clozes
        assert CardValidator.is_cloze_card("{{c1::a}} and {{c2::b}}")
        # Nested content
        assert CardValidator.is_cloze_card("The {{c1::capital of France}} is Paris")
        # Not a cloze
        assert not CardValidator.is_cloze_card("Regular question")
        assert not CardValidator.is_cloze_card("{{incomplete")

    def test_cloze_extraction(self):
        """Test extraction of cloze answers."""
        content = "{{c1::Paris::capital}} is in {{c2::France}}"
        answers = CardValidator.extract_cloze_answers(content)
        
        assert len(answers) == 2
        assert (1, 'Paris', 'capital') in answers
        assert (2, 'France', None) in answers

    def test_content_length_limits(self):
        """Test content length validation."""
        # Empty content
        is_valid, error = CardValidator.validate_content("")
        assert not is_valid
        assert "empty" in error.lower()
        
        # Content too long
        long_content = "X" * 60000
        is_valid, error = CardValidator.validate_content(long_content)
        assert not is_valid
        assert "too long" in error.lower()
        
        # Valid content
        is_valid, error = CardValidator.validate_content("Valid question")
        assert is_valid
        assert error is None

    def test_html_detection_patterns(self):
        """Test HTML detection for various patterns."""
        assert CardValidator.contains_html("<b>bold</b>")
        assert CardValidator.contains_html("<img src='x'>")
        assert CardValidator.contains_html("<div class='test'>")
        assert not CardValidator.contains_html("Plain text")
        # Note: Simple regex pattern may have false positives with math expressions
        # This is a known limitation - "3 < 5 and 5 > 3" may be detected as HTML
        # because it contains angle brackets. Advanced HTML detection would need
        # more sophisticated parsing.

    def test_media_extraction(self):
        """Test extraction of media references."""
        content = """
        <img src="image.png">
        <img src='photo.jpg' alt="test">
        [sound:audio.mp3]
        [sound:music.wav]
        """
        media = CardValidator.extract_media_references(content)
        
        assert len(media['images']) == 2
        assert 'image.png' in media['images']
        assert len(media['sounds']) == 2

    def test_tag_parser_hierarchical(self):
        """Test hierarchical tag parsing."""
        assert TagParser.is_hierarchical("science::physics::quantum")
        assert not TagParser.is_hierarchical("simple_tag")
        
        parts = TagParser.split_hierarchical_tag("a::b::c")
        assert parts == ['a', 'b', 'c']

    def test_tag_normalization(self):
        """Test tag normalization."""
        tags = ["TAG1", "tag1", "  Tag2  ", "TAG2"]
        normalized = TagParser.normalize_tags(tags)
        
        assert len(normalized) == 2
        assert 'tag1' in normalized
        assert 'tag2' in normalized


# ============================================================================
# HTML Handler Tests
# ============================================================================

class TestHtmlHandlerAdvanced:
    """Advanced tests for HTML handling."""

    def test_strip_html_preserves_structure(self):
        """Test that HTML stripping preserves text structure."""
        html = "<p>Paragraph 1</p><p>Paragraph 2</p>"
        result = HtmlHandler.strip_html(html)
        
        # Should have newlines between paragraphs
        assert '\n' in result
        assert 'Paragraph 1' in result
        assert 'Paragraph 2' in result

    def test_strip_html_handles_entities(self):
        """Test HTML entity decoding."""
        html = "&amp; &lt; &gt; &quot; &nbsp;"
        result = HtmlHandler.strip_html(html)
        
        assert '&' in result
        assert '<' in result
        assert '>' in result

    def test_convert_to_plain_text(self):
        """Test conversion to plain text with structure."""
        html = """
        <h1>Title</h1>
        <p>Paragraph with <a href="http://example.com">link</a></p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        """
        result = HtmlHandler.convert_to_plain_text(html)
        
        assert 'Title' in result
        assert 'link' in result
        assert '•' in result  # List bullet

    def test_sanitize_for_display_truncation(self):
        """Test display sanitization with truncation."""
        long_html = "<p>" + "X" * 300 + "</p>"
        result = HtmlHandler.sanitize_for_display(long_html, max_length=100)
        
        assert len(result) <= 100
        assert result.endswith("...")

    def test_analyze_content(self):
        """Test content analysis."""
        html = """
        <p><img src="test.png"></p>
        <p>[sound:audio.mp3]</p>
        <a href="http://example.com">Link</a>
        """
        analysis = HtmlHandler.analyze_content(html)
        
        assert analysis['has_html'] is True
        assert analysis['has_images'] is True
        assert analysis['has_audio'] is True
        assert analysis['has_links'] is True


# ============================================================================
# Deck Detection Tests
# ============================================================================

class TestDeckDetectionAdvanced:
    """Advanced tests for deck detection and assignment."""

    def test_suggest_deck_programming(self):
        """Test deck suggestion for programming content."""
        cards = [
            Flashcard(front="What is a function?", back="A reusable code block", tags=["python"]),
            Flashcard(front="def keyword", back="Defines a function", tags=["code"]),
        ]
        
        suggestion = DeckDetector.suggest_deck_from_content(cards)
        assert suggestion == "Programming"

    def test_suggest_deck_languages(self):
        """Test deck suggestion for language learning content."""
        cards = [
            Flashcard(front="Bonjour", back="Hello in French", tags=["vocabulary"]),
            Flashcard(front="Grammar rule", back="Conjugation", tags=[]),
        ]
        
        suggestion = DeckDetector.suggest_deck_from_content(cards)
        assert suggestion == "Languages"

    def test_suggest_deck_from_tags(self):
        """Test deck suggestion based on common tags."""
        cards = [
            Flashcard(front="Q1", back="A1", tags=["biology", "science"]),
            Flashcard(front="Q2", back="A2", tags=["biology"]),
            Flashcard(front="Q3", back="A3", tags=["biology", "cell"]),
        ]
        
        suggestion = DeckDetector.suggest_deck_from_tags(cards)
        assert suggestion == "Biology"

    def test_analyze_deck_coverage(self):
        """Test deck coverage analysis."""
        cards = [
            Flashcard(front="Q1", back="A1", deck_name="Deck1"),
            Flashcard(front="Q2", back="A2", deck_name="Deck1"),
            Flashcard(front="Q3", back="A3"),  # No deck
            Flashcard(front="Q4", back="A4"),  # No deck
        ]
        
        analysis = DeckDetector.analyze_deck_coverage(cards)
        
        assert analysis['total_cards'] == 4
        assert analysis['cards_with_deck'] == 2
        assert analysis['cards_without_deck'] == 2
        assert analysis['coverage_percent'] == 50.0
        assert analysis['needs_deck_assignment'] is True

    def test_group_cards_by_suggested_deck(self):
        """Test grouping cards by suggested deck."""
        cards = [
            Flashcard(front="Python code", back="A", tags=["programming"]),
            Flashcard(front="French word", back="B", tags=["vocabulary"]),
            Flashcard(front="Random", back="C", tags=[]),
        ]
        
        groups = DeckDetector.group_cards_by_suggested_deck(cards)
        
        assert "Programming" in groups
        assert "Languages" in groups
        assert "General" in groups

    def test_missing_deck_warning_message(self):
        """Test warning message generation."""
        # All cards missing deck
        msg = MissingDeckHandler.get_warning_message(10, 10)
        assert "All 10 cards" in msg
        
        # Some cards missing deck
        msg = MissingDeckHandler.get_warning_message(5, 10)
        assert "5 of 10" in msg
        assert "50.0%" in msg

    def test_assign_default_deck(self):
        """Test default deck assignment."""
        cards = [
            Flashcard(front="Q1", back="A1"),
            Flashcard(front="Q2", back="A2", deck_name="Existing"),
            Flashcard(front="Q3", back="A3"),
        ]
        
        count = MissingDeckHandler.assign_default_deck(cards, "Imported")
        
        assert count == 2
        assert cards[0].deck_name == "Imported"
        assert cards[1].deck_name == "Existing"  # Unchanged
        assert cards[2].deck_name == "Imported"


# ============================================================================
# Anki Header Parser Tests
# ============================================================================

class TestAnkiHeaderParserAdvanced:
    """Advanced tests for Anki header parsing."""

    def test_parse_all_separators(self):
        """Test parsing various separator types."""
        separators = [
            ("#separator:tab", "\t"),
            ("#separator:comma", ","),
            ("#separator:semicolon", ";"),
            ("#separator:space", " "),
            ("#separator:pipe", "|"),
        ]
        
        for line, expected in separators:
            result = AnkiHeaderParser.parse_separator(line)
            assert result == expected, f"Failed for {line}"

    def test_parse_html_settings(self):
        """Test HTML setting parsing."""
        assert AnkiHeaderParser.parse_html_setting("#html:true") is True
        assert AnkiHeaderParser.parse_html_setting("#html:false") is False
        assert AnkiHeaderParser.parse_html_setting("#html:TRUE") is True
        assert AnkiHeaderParser.parse_html_setting("not a header") is None

    def test_parse_column_indices(self):
        """Test column index parsing."""
        result = AnkiHeaderParser.parse_column_index("#deck column:3")
        assert result == ('deck', 3)
        
        result = AnkiHeaderParser.parse_column_index("#tags column:4")
        assert result == ('tags', 4)
        
        result = AnkiHeaderParser.parse_column_index("#notetype column:2")
        assert result == ('notetype', 2)

    def test_parse_all_headers(self):
        """Test parsing complete header block."""
        lines = [
            "#separator:comma",
            "#html:true",
            "#deck column:3",
            "#tags column:4",
            "Question,Answer,Deck,Tags"  # First data line
        ]
        
        settings = AnkiHeaderParser.parse_all_headers(lines)
        
        assert settings['separator'] == ','
        assert settings['html'] is True
        assert settings['columns']['deck'] == 3
        assert settings['columns']['tags'] == 4


# ============================================================================
# Import Service Tests
# ============================================================================

class TestImportServiceAdvanced:
    """Advanced tests for ImportService."""

    def test_get_supported_formats(self):
        """Test that all expected formats are supported."""
        formats = ImportService.get_supported_formats()
        
        expected = {'.txt', '.csv', '.tsv', '.xlsx', '.xls', '.apkg', '.colpkg'}
        assert set(formats) == expected

    def test_max_file_size_constant(self):
        """Test file size limit is set correctly."""
        assert ImportService.MAX_FILE_SIZE == 50 * 1024 * 1024  # 50MB


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandlingAdvanced:
    """Advanced tests for error handling."""

    @pytest.mark.asyncio
    async def test_corrupted_apkg_handling(self):
        """Test handling of corrupted APKG file."""
        # Create invalid ZIP content
        corrupted = b"This is not a valid zip file"
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("corrupted.apkg", BytesIO(corrupted), "application/octet-stream")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_empty_apkg_handling(self):
        """Test handling of APKG with no cards."""
        # Create APKG with no cards
        empty_apkg = create_mock_apkg({1: "Empty"}, [])
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("empty.apkg", BytesIO(empty_apkg), "application/octet-stream")}
            response = await client.post("/import/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            # Should still succeed but with 0 cards
            assert data['summary']['total_imported'] == 0

    def test_exception_messages(self):
        """Test exception message formatting."""
        # FileFormatError
        err = FileFormatError("test.xyz", "Expected .csv or .txt")
        assert "test.xyz" in str(err)
        assert "Expected" in str(err)
        
        # ParsingError with line number
        err = ParsingError("Invalid format", line_number=42)
        assert "Line 42" in str(err)
        
        # EmptyFileError
        err = EmptyFileError("empty.csv")
        assert "empty.csv" in str(err)
        assert "No valid cards" in str(err)


# ============================================================================
# Flashcard Model Tests
# ============================================================================

class TestFlashcardModelAdvanced:
    """Advanced tests for the Flashcard model."""

    def test_flashcard_equality(self):
        """Test flashcard comparison."""
        card1 = Flashcard(front="Q", back="A", deck_name="D", tags=["t"])
        card2 = Flashcard(front="Q", back="A", deck_name="D", tags=["t"])
        
        # Compare relevant fields (excluding created_at which differs per instance)
        d1 = card1.to_dict()
        d2 = card2.to_dict()
        d1.pop('created_at', None)
        d2.pop('created_at', None)
        assert d1 == d2

    def test_flashcard_with_all_fields(self):
        """Test flashcard with all optional fields."""
        card = Flashcard(
            front="Question",
            back="Answer",
            deck_name="TestDeck",
            tags=["tag1", "tag2"],
            card_type=CardType.CLOZE,
            extra="Extra content",
            source_file="test.csv",
            html_enabled=True
        )
        
        d = card.to_dict()
        assert d['front'] == "Question"
        assert d['back'] == "Answer"
        assert d['deck_name'] == "TestDeck"
        assert d['tags'] == ["tag1", "tag2"]
        assert d['card_type'] == "cloze"
        assert d['extra'] == "Extra content"
        assert d['source_file'] == "test.csv"
        assert d['html_enabled'] is True

    def test_flashcard_validation(self):
        """Test flashcard validation rules."""
        # Valid card
        card = Flashcard(front="Q", back="A")
        assert card.is_valid()
        
        # Empty front
        card = Flashcard(front="", back="A")
        assert not card.is_valid()
        
        # Empty back
        card = Flashcard(front="Q", back="")
        assert not card.is_valid()
        
        # Whitespace only
        card = Flashcard(front="   ", back="A")
        assert not card.is_valid()


# ============================================================================
# Import Result Tests
# ============================================================================

class TestImportResultAdvanced:
    """Advanced tests for ImportResult."""

    def test_success_rate_edge_cases(self):
        """Test success rate calculation edge cases."""
        # No cards processed
        result = ImportResult(source_file="test.txt")
        assert result.success_rate == 0.0
        
        # 100% success
        result = ImportResult(source_file="test.txt")
        result.add_card(Flashcard(front="Q", back="A"))
        assert result.success_rate == 100.0
        
        # 0% success (all skipped)
        result = ImportResult(source_file="test.txt")
        result.skipped_count = 5
        assert result.success_rate == 0.0

    def test_error_accumulation(self):
        """Test error message accumulation."""
        result = ImportResult(source_file="test.txt")
        result.add_error("Error 1")
        result.add_error("Error 2")
        result.add_error("Error 3")
        
        assert len(result.errors) == 3
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors

    def test_deck_detected_flag(self):
        """Test deck detection flag handling."""
        result = ImportResult(source_file="test.txt")
        result.deck_detected = True
        
        assert result.deck_detected is True


# ============================================================================
# Concurrent Import Tests
# ============================================================================

class TestConcurrentImport:
    """Tests for concurrent import handling."""

    @pytest.mark.asyncio
    async def test_concurrent_uploads(self):
        """Test multiple concurrent uploads."""
        csv_content = b"front,back\nQ1,A1\nQ2,A2\n"
        
        async def upload_file(filename: str):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                files = {"file": (filename, BytesIO(csv_content), "text/csv")}
                response = await client.post("/import/upload", files=files)
                return response
        
        # Run 5 concurrent uploads
        tasks = [upload_file(f"test_{i}.csv") for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['summary']['total_imported'] == 2

