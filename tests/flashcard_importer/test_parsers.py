"""Unit tests for the flashcard importer parsers."""
import pytest

from flashcard_importer import Flashcard, ImportResult, CardType, ParserFactory
from flashcard_importer.parsers import TxtParser, CsvParser
from flashcard_importer.exceptions import FileFormatError


class TestParserFactory:
    """Tests for ParserFactory."""

    def test_supported_formats(self):
        """Test that all expected formats are supported."""
        formats = ParserFactory.get_supported_formats()
        assert '.txt' in formats
        assert '.csv' in formats
        assert '.tsv' in formats
        assert '.xlsx' in formats
        assert '.apkg' in formats

    def test_create_txt_parser(self, tmp_path):
        """Test creating a TXT parser."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("front\tback\n")
        parser = ParserFactory.create(str(test_file))
        assert isinstance(parser, TxtParser)

    def test_create_csv_parser(self, tmp_path):
        """Test creating a CSV parser."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("front,back\n")
        parser = ParserFactory.create(str(test_file))
        assert isinstance(parser, CsvParser)

    def test_unsupported_format(self, tmp_path):
        """Test that unsupported formats raise FileFormatError."""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("content")
        with pytest.raises(FileFormatError):
            ParserFactory.create(str(test_file))

    def test_file_not_found(self):
        """Test that missing files raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ParserFactory.create("nonexistent.txt")


class TestTxtParser:
    """Tests for TxtParser."""

    def test_simple_txt(self, tmp_path):
        """Test parsing a simple tab-separated file."""
        test_file = tmp_path / "simple.txt"
        test_file.write_text("What is Python?\tA programming language\n")
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 1
        assert result.cards[0].front == "What is Python?"
        assert result.cards[0].back == "A programming language"

    def test_anki_headers(self, tmp_path):
        """Test parsing file with Anki headers."""
        test_file = tmp_path / "anki.txt"
        test_file.write_text(
            "#separator:tab\n"
            "#html:true\n"
            "#deck column:3\n"
            "Question\tAnswer\tMyDeck\n"
        )
        parser = TxtParser(str(test_file))
        settings = parser.detect_settings()
        assert settings['separator'] == '\t'
        assert settings['html'] is True
        assert settings['columns']['deck'] == 3

    def test_skip_empty_lines(self, tmp_path):
        """Test that empty lines are skipped."""
        test_file = tmp_path / "with_empty.txt"
        test_file.write_text("Q1\tA1\n\n\nQ2\tA2\n")
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 2

    def test_cloze_detection(self, tmp_path):
        """Test cloze card detection."""
        test_file = tmp_path / "cloze.txt"
        test_file.write_text("The {{c1::answer}} is here\tBack\n")
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert result.cards[0].card_type == CardType.CLOZE


class TestCsvParser:
    """Tests for CsvParser."""

    def test_simple_csv(self, tmp_path):
        """Test parsing a simple CSV file."""
        test_file = tmp_path / "simple.csv"
        test_file.write_text("Q1,A1\nQ2,A2\n")
        parser = CsvParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 2

    def test_csv_with_headers(self, tmp_path):
        """Test parsing CSV with header row."""
        test_file = tmp_path / "with_headers.csv"
        test_file.write_text(
            "front,back,deck,tags\n"
            "Q1,A1,MyDeck,tag1\n"
            "Q2,A2,MyDeck,tag2\n"
            "Q3,A3,MyDeck,tag3\n"
            "Q4,A4,MyDeck,tag4\n"
        )
        parser = CsvParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 4
        assert result.cards[0].deck_name == "MyDeck"

    def test_tsv_file(self, tmp_path):
        """Test parsing TSV file."""
        test_file = tmp_path / "test.tsv"
        test_file.write_text("Q1\tA1\nQ2\tA2\n")
        parser = CsvParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 2

    def test_custom_column_mapping(self, tmp_path):
        """Test custom column mapping."""
        test_file = tmp_path / "custom.csv"
        test_file.write_text("A1,Q1,Deck1\nA2,Q2,Deck2\n")
        parser = CsvParser(str(test_file), has_header=False)
        parser.set_column_mapping(front=1, back=0, deck=2)
        result = parser.parse()
        assert result.cards[0].front == "Q1"
        assert result.cards[0].back == "A1"
        assert result.cards[0].deck_name == "Deck1"


class TestFlashcard:
    """Tests for Flashcard dataclass."""

    def test_create_flashcard(self):
        """Test creating a flashcard."""
        card = Flashcard(
            front="Question",
            back="Answer",
            deck_name="MyDeck",
            tags=["tag1", "tag2"]
        )
        assert card.front == "Question"
        assert card.back == "Answer"
        assert card.deck_name == "MyDeck"
        assert card.tags == ["tag1", "tag2"]

    def test_invalid_flashcard_empty_front(self):
        """Test that empty front is detected as invalid."""
        card = Flashcard(front="", back="Answer")
        assert not card.is_valid()

    def test_invalid_flashcard_empty_back(self):
        """Test that empty back is detected as invalid."""
        card = Flashcard(front="Question", back="")
        assert not card.is_valid()

    def test_to_dict(self):
        """Test converting flashcard to dictionary."""
        card = Flashcard(
            front="Q",
            back="A",
            deck_name="Deck",
            tags=["tag"]
        )
        d = card.to_dict()
        assert d['front'] == "Q"
        assert d['back'] == "A"
        assert d['deck_name'] == "Deck"
        assert d['tags'] == ["tag"]

    def test_whitespace_stripping(self):
        """Test that whitespace is properly handled."""
        card = Flashcard(front="  Question  ", back="  Answer  ")
        assert card.is_valid()


class TestImportResult:
    """Tests for ImportResult."""

    def test_add_card(self):
        """Test adding cards to result."""
        result = ImportResult(source_file="test.txt")
        result.add_card(Flashcard(front="Q", back="A"))
        assert len(result.cards) == 1

    def test_add_error(self):
        """Test adding errors to result."""
        result = ImportResult(source_file="test.txt")
        result.add_error("Error message")
        assert len(result.errors) == 1

    def test_success_rate(self):
        """Test success rate calculation."""
        result = ImportResult(source_file="test.txt")
        result.add_card(Flashcard(front="Q1", back="A1"))
        result.add_card(Flashcard(front="Q2", back="A2"))
        result.skipped_count = 1
        assert result.success_rate == pytest.approx(66.67, rel=0.01)

    def test_total_processed(self):
        """Test total processed count."""
        result = ImportResult(source_file="test.txt")
        result.add_card(Flashcard(front="Q", back="A"))
        result.skipped_count = 2
        assert result.total_processed == 3


class TestEdgeCases:
    """Tests for edge cases."""

    def test_malformed_line_skipped(self, tmp_path):
        """Test that malformed lines are skipped with error."""
        test_file = tmp_path / "malformed.txt"
        test_file.write_text("Valid\tAnswer\nOnlyOnePart\nAnother\tValid\n")
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 2
        assert len(result.errors) == 1

    def test_empty_file(self, tmp_path):
        """Test handling empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 0
        # Empty file produces error and counts as skipped
        assert len(result.errors) >= 1

    def test_unicode_content(self, tmp_path):
        """Test handling unicode content."""
        test_file = tmp_path / "unicode.txt"
        test_file.write_text("日本語\t日本語の答え\n", encoding='utf-8')
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert len(result.cards) == 1
        assert result.cards[0].front == "日本語"

    def test_html_content_detection(self, tmp_path):
        """Test HTML content detection."""
        test_file = tmp_path / "html.txt"
        test_file.write_text("<b>Bold</b>\t<i>Italic</i>\n")
        parser = TxtParser(str(test_file))
        result = parser.parse()
        assert result.cards[0].html_enabled is True
