import csv
from pathlib import Path
from typing import Union, Optional

from flashcard_importer.models.flashcard import Flashcard, ImportResult, CardType
from flashcard_importer.parsers.base import BaseParser, ParserFactory
from flashcard_importer.utils.validators import CardValidator


class CsvParser(BaseParser):
    """Parser for CSV/TSV files."""
    
    SUPPORTED_EXTENSIONS = ['.csv', '.tsv']
    
    def __init__(self, file_path: Union[str, Path], delimiter: str = None, has_header: bool = None):
        super().__init__(file_path)
        self._delimiter = delimiter
        self._has_header = has_header
        self.settings = {}
        self.column_mapping = {}
    
    def detect_settings(self) -> dict:
        """Auto-detect CSV settings (delimiter, headers)."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            sample = f.read(4096)
        
        # Use csv.Sniffer to detect dialect
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            detected_delimiter = dialect.delimiter
        except csv.Error:
            # Default based on extension
            detected_delimiter = '\t' if self.file_path.suffix.lower() == '.tsv' else ','
        
        # Detect if first row is header by checking common header names
        has_header = False
        try:
            first_line = sample.split('\n')[0].lower()
            header_keywords = ['front', 'back', 'question', 'answer', 'term', 'definition', 
                             'deck', 'tags', 'category', 'word', 'meaning']
            has_header = any(kw in first_line for kw in header_keywords)
        except:
            pass
        
        # Fall back to csv.Sniffer if keyword detection didn't find headers
        if not has_header:
            try:
                has_header = csv.Sniffer().has_header(sample)
            except csv.Error:
                has_header = False
        
        self.settings = {
            'delimiter': self._delimiter or detected_delimiter,
            'has_header': self._has_header if self._has_header is not None else has_header,
        }
        
        return self.settings
    
    def set_column_mapping(self, front: int = 0, back: int = 1, deck: int = None, tags: int = None):
        """Set which columns contain which data (0-based index)."""
        self.column_mapping = {
            'front': front,
            'back': back,
            'deck': deck,
            'tags': tags
        }
    
    def parse(self) -> ImportResult:
        """Parse the CSV file and return flashcards."""
        result = ImportResult(source_file=str(self.file_path))
        
        # Detect settings if not already done
        if not self.settings:
            self.detect_settings()
        
        delimiter = self.settings.get('delimiter', ',')
        has_header = self.settings.get('has_header', False)
        
        # Default column mapping
        if not self.column_mapping:
            self.column_mapping = {'front': 0, 'back': 1, 'deck': None, 'tags': None}
        
        result.deck_detected = self.column_mapping.get('deck') is not None
        
        with open(self.file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=delimiter)
            
            # Skip header row if present
            if has_header:
                header_row = next(reader, None)
                if header_row:
                    self._detect_columns_from_header(header_row)
            
            for line_num, row in enumerate(reader, start=2 if has_header else 1):
                # Skip empty rows
                if not row or all(not cell.strip() for cell in row):
                    continue
                
                card = self._parse_row(row, line_num, result)
                if card:
                    result.add_card(card)
        
        if not result.cards:
            result.add_error("No valid cards found in file")
        
        return result
    
    def _detect_columns_from_header(self, header_row: list):
        """Try to detect column mapping from header names."""
        header_lower = [h.lower().strip() for h in header_row]
        
        # Common column name patterns
        front_names = ['front', 'question', 'q', 'term', 'word']
        back_names = ['back', 'answer', 'a', 'definition', 'meaning']
        deck_names = ['deck', 'category', 'collection', 'group']
        tag_names = ['tags', 'tag', 'labels', 'keywords']
        
        for i, name in enumerate(header_lower):
            if name in front_names:
                self.column_mapping['front'] = i
            elif name in back_names:
                self.column_mapping['back'] = i
            elif name in deck_names:
                self.column_mapping['deck'] = i
            elif name in tag_names:
                self.column_mapping['tags'] = i
    
    def _parse_row(self, row: list, line_num: int, result: ImportResult) -> Optional[Flashcard]:
        """Parse a single row into a Flashcard."""
        
        front_col = self.column_mapping.get('front', 0)
        back_col = self.column_mapping.get('back', 1)
        deck_col = self.column_mapping.get('deck')
        tags_col = self.column_mapping.get('tags')
        
        # Check we have enough columns
        if len(row) <= max(front_col, back_col):
            result.add_error(f"Line {line_num}: Not enough columns")
            return None
        
        front = row[front_col].strip()
        back = row[back_col].strip()
        
        # Validate content
        is_valid, error = CardValidator.validate_content(front)
        if not is_valid:
            result.add_error(f"Line {line_num}: Front - {error}")
            return None
        
        is_valid, error = CardValidator.validate_content(back)
        if not is_valid:
            result.add_error(f"Line {line_num}: Back - {error}")
            return None
        
        # Extract optional fields
        deck_name = None
        tags = []
        
        if deck_col is not None and deck_col < len(row):
            deck_name = row[deck_col].strip() or None
        
        if tags_col is not None and tags_col < len(row):
            tag_string = row[tags_col].strip()
            if tag_string:
                # Tags might be comma or space separated
                if ',' in tag_string:
                    tags = [t.strip() for t in tag_string.split(',') if t.strip()]
                else:
                    tags = tag_string.split()
        
        # Detect card type
        card_type = CardType.CLOZE if CardValidator.is_cloze_card(front) else CardType.BASIC
        
        return Flashcard(
            front=front,
            back=back,
            deck_name=deck_name,
            tags=tags,
            card_type=card_type,
            source_file=str(self.file_path),
            html_enabled=CardValidator.contains_html(front) or CardValidator.contains_html(back)
        )


# Register the parser
ParserFactory.register('.csv', CsvParser)
ParserFactory.register('.tsv', CsvParser)

