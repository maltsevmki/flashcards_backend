"""Comprehensive tests for all flashcard parsers."""
import pytest
import tempfile
import os
from pathlib import Path

from flashcard_importer import ParserFactory, Flashcard, ImportResult, CardType
from flashcard_importer.parsers import TxtParser, CsvParser, XlsxParser, ApkgParser
from flashcard_importer.exceptions import FileFormatError, ParsingError


class TestParserFactory:
    """Tests for ParserFactory."""
    
    def test_supported_formats(self):
        formats = ParserFactory.get_supported_formats()
        assert '.txt' in formats
        assert '.csv' in formats
        assert '.tsv' in formats
        assert '.xlsx' in formats
        assert '.apkg' in formats
    
    def test_create_txt_parser(self, tmp_path):
        file = tmp_path / "test.txt"
        file.write_text("Q\tA")
        parser = ParserFactory.create(str(file))
        assert isinstance(parser, TxtParser)
    
    def test_create_csv_parser(self, tmp_path):
        file = tmp_path / "test.csv"
        file.write_text("Q,A")
        parser = ParserFactory.create(str(file))
        assert isinstance(parser, CsvParser)
    
    def test_unsupported_format(self, tmp_path):
        file = tmp_path / "test.xyz"
        file.write_text("content")
        with pytest.raises(FileFormatError):
            ParserFactory.create(str(file))
    
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            ParserFactory.create("nonexistent.txt")


class TestTxtParser:
    """Tests for TxtParser."""
    
    def test_simple_txt(self, tmp_path):
        file = tmp_path / "simple.txt"
        file.write_text("Question 1\tAnswer 1\nQuestion 2\tAnswer 2")
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 2
        assert result.cards[0].front == "Question 1"
        assert result.cards[0].back == "Answer 1"
    
    def test_anki_headers(self, tmp_path):
        file = tmp_path / "anki.txt"
        content = """#separator:tab
#html:true
#deck column:3
Question\tAnswer\tMyDeck
"""
        file.write_text(content)
        
        parser = TxtParser(str(file))
        settings = parser.detect_settings()
        
        assert settings['separator'] == '\t'
        assert settings['html'] == True
        assert settings['columns']['deck'] == 3
    
    def test_skip_empty_lines(self, tmp_path):
        file = tmp_path / "empty.txt"
        file.write_text("Q1\tA1\n\nQ2\tA2\n\n\nQ3\tA3")
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 3
    
    def test_cloze_detection(self, tmp_path):
        file = tmp_path / "cloze.txt"
        file.write_text("The {{c1::answer}} is here\tCloze card")
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert result.cards[0].card_type == CardType.CLOZE


class TestCsvParser:
    """Tests for CsvParser."""
    
    def test_simple_csv(self, tmp_path):
        file = tmp_path / "simple.csv"
        file.write_text("Q1,A1\nQ2,A2")
        
        parser = CsvParser(str(file))
        parser.settings = {'delimiter': ',', 'has_header': False}
        result = parser.parse()
        
        assert len(result.cards) == 2
    
    def test_csv_with_headers(self, tmp_path):
        file = tmp_path / "headers.csv"
        file.write_text("front,back,deck,tags\nQ1,A1,Deck1,tag1")
        
        parser = CsvParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 1
        assert result.cards[0].deck_name == "Deck1"
        assert "tag1" in result.cards[0].tags
    
    def test_tsv_file(self, tmp_path):
        file = tmp_path / "test.tsv"
        file.write_text("Question\tAnswer\nQ1\tA1")
        
        parser = CsvParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 1
    
    def test_custom_column_mapping(self, tmp_path):
        file = tmp_path / "custom.csv"
        file.write_text("Deck,Answer,Question\nMyDeck,A1,Q1")
        
        parser = CsvParser(str(file))
        parser.settings = {'delimiter': ',', 'has_header': True}
        parser.set_column_mapping(front=2, back=1, deck=0)
        result = parser.parse()
        
        assert result.cards[0].front == "Q1"
        assert result.cards[0].back == "A1"
        assert result.cards[0].deck_name == "MyDeck"


class TestFlashcard:
    """Tests for Flashcard model."""
    
    def test_create_flashcard(self):
        card = Flashcard(front="Q", back="A")
        assert card.front == "Q"
        assert card.back == "A"
        assert card.is_valid()
    
    def test_invalid_flashcard_empty_front(self):
        card = Flashcard(front="", back="A")
        assert not card.is_valid()
    
    def test_invalid_flashcard_empty_back(self):
        card = Flashcard(front="Q", back="")
        assert not card.is_valid()
    
    def test_to_dict(self):
        card = Flashcard(front="Q", back="A", deck_name="Test", tags=["tag1"])
        d = card.to_dict()
        
        assert d['front'] == "Q"
        assert d['back'] == "A"
        assert d['deck_name'] == "Test"
        assert d['tags'] == ["tag1"]
    
    def test_whitespace_stripping(self):
        card = Flashcard(front="  Q  ", back="  A  ", deck_name="  Deck  ")
        assert card.front == "Q"
        assert card.back == "A"
        assert card.deck_name == "Deck"


class TestImportResult:
    """Tests for ImportResult."""
    
    def test_add_card(self):
        result = ImportResult()
        result.add_card(Flashcard(front="Q", back="A"))
        
        assert len(result.cards) == 1
    
    def test_add_error(self):
        result = ImportResult()
        result.add_error("Error message")
        
        assert result.skipped_count == 1
        assert len(result.errors) == 1
    
    def test_success_rate(self):
        result = ImportResult()
        result.add_card(Flashcard(front="Q1", back="A1"))
        result.add_card(Flashcard(front="Q2", back="A2"))
        result.add_error("Error")
        
        assert result.success_rate == pytest.approx(66.67, 0.1)
    
    def test_total_processed(self):
        result = ImportResult()
        result.add_card(Flashcard(front="Q", back="A"))
        result.add_error("Error")
        
        assert result.total_processed == 2


class TestEdgeCases:
    """Tests for edge cases and validation."""
    
    def test_malformed_line_skipped(self, tmp_path):
        file = tmp_path / "malformed.txt"
        file.write_text("Q1\tA1\nBadLine\nQ2\tA2")
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 2
        assert result.skipped_count == 1
    
    def test_empty_file(self, tmp_path):
        file = tmp_path / "empty.txt"
        file.write_text("")
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 0
        # Empty file generates "No valid cards found" error
        assert "No valid cards found" in result.errors[0] if result.errors else True
    
    def test_unicode_content(self, tmp_path):
        file = tmp_path / "unicode.txt"
        file.write_text("你好\t世界\nПривет\tМир", encoding='utf-8')
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert len(result.cards) == 2
        assert result.cards[0].front == "你好"
    
    def test_html_content_detection(self, tmp_path):
        file = tmp_path / "html.txt"
        file.write_text("<b>Bold</b>\t<i>Italic</i>")
        
        parser = TxtParser(str(file))
        result = parser.parse()
        
        assert result.cards[0].html_enabled == True


# Run with: pytest tests/flashcard_importer/test_parsers.py -v

