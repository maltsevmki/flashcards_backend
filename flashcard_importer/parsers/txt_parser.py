from pathlib import Path
from typing import Union, List, Optional

from flashcard_importer.models.flashcard import Flashcard, ImportResult, CardType
from flashcard_importer.parsers.base import BaseParser, ParserFactory
from flashcard_importer.utils.validators import AnkiHeaderParser, CardValidator
from flashcard_importer.exceptions import ParsingError, EmptyFileError


class TxtParser(BaseParser):
    """Parser for Anki TXT export files."""
    
    SUPPORTED_EXTENSIONS = ['.txt']
    
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.settings = {}
        self.header_lines_count = 0
    
    def detect_settings(self) -> dict:
        """Detect Anki headers and file settings."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.settings = AnkiHeaderParser.parse_all_headers(lines)
        
        # Count header lines
        self.header_lines_count = 0
        for line in lines:
            if AnkiHeaderParser.is_header_line(line):
                self.header_lines_count += 1
            else:
                break
        
        return self.settings
    
    def parse(self) -> ImportResult:
        """Parse the TXT file and return flashcards."""
        result = ImportResult(source_file=str(self.file_path))
        
        # Detect settings first
        self.detect_settings()
        
        separator = self.settings.get('separator', '\t')
        html_enabled = self.settings.get('html', False)
        columns = self.settings.get('columns', {})
        
        # Check if deck column is specified
        result.deck_detected = 'deck' in columns
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Skip header lines
        data_lines = lines[self.header_lines_count:]
        
        for line_num, line in enumerate(data_lines, start=self.header_lines_count + 1):
            line = line.rstrip('\n\r')
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Parse the line
            card = self._parse_line(line, line_num, separator, html_enabled, columns, result)
            if card:
                result.add_card(card)
        
        if not result.cards:
            result.add_error("No valid cards found in file")
        
        return result
    
    def _parse_line(
        self, 
        line: str, 
        line_num: int, 
        separator: str,
        html_enabled: bool,
        columns: dict,
        result: ImportResult
    ) -> Optional[Flashcard]:
        """Parse a single line into a Flashcard."""
        
        parts = line.split(separator)
        
        # Need at least 2 parts (front and back)
        if len(parts) < 2:
            result.add_error(f"Line {line_num}: Not enough fields (need at least front and back)")
            return None
        
        # Default: first column is front, second is back
        front = parts[0].strip()
        back = parts[1].strip()
        
        # Validate content
        is_valid, error = CardValidator.validate_content(front)
        if not is_valid:
            result.add_error(f"Line {line_num}: Front field - {error}")
            return None
        
        is_valid, error = CardValidator.validate_content(back)
        if not is_valid:
            result.add_error(f"Line {line_num}: Back field - {error}")
            return None
        
        # Extract optional fields based on column settings
        deck_name = None
        tags = []
        
        if 'deck' in columns:
            deck_col = columns['deck'] - 1  # Convert to 0-based index
            if deck_col < len(parts):
                deck_name = parts[deck_col].strip() or None
        
        if 'tags' in columns:
            tags_col = columns['tags'] - 1
            if tags_col < len(parts):
                tag_string = parts[tags_col].strip()
                if tag_string:
                    tags = tag_string.split()
        
        # Detect card type
        card_type = CardType.CLOZE if CardValidator.is_cloze_card(front) else CardType.BASIC
        
        # Detect HTML content - either from header setting or actual content
        has_html = html_enabled or CardValidator.contains_html(front) or CardValidator.contains_html(back)
        
        return Flashcard(
            front=front,
            back=back,
            deck_name=deck_name,
            tags=tags,
            card_type=card_type,
            source_file=str(self.file_path),
            html_enabled=has_html
        )


# Register the parser
ParserFactory.register('.txt', TxtParser)

