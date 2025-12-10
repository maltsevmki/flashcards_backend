import zipfile
import sqlite3
import tempfile
import shutil
import json
import os
from pathlib import Path
from typing import Union, Optional, List, Dict

from flashcard_importer.models.flashcard import Flashcard, ImportResult, CardType
from flashcard_importer.parsers.base import BaseParser, ParserFactory
from flashcard_importer.utils.validators import CardValidator
from flashcard_importer.exceptions import AnkiDatabaseError


class ApkgParser(BaseParser):
    """
    Parser for Anki package files (.apkg and .colpkg).
    These are ZIP files containing a SQLite database.
    """
    
    SUPPORTED_EXTENSIONS = ['.apkg', '.colpkg']
    
    # Possible database filenames inside the package
    DB_FILENAMES = ['collection.anki2', 'collection.anki21', 'collection.anki2b']
    
    def __init__(self, file_path: Union[str, Path]):
        super().__init__(file_path)
        self.settings = {}
        self._temp_dir = None
        self._db_path = None
    
    def __del__(self):
        self._cleanup()
    
    def _cleanup(self):
        """Clean up temporary files."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except:
                pass
    
    def _extract_database(self) -> str:
        """Extract the SQLite database from the ZIP file."""
        self._temp_dir = tempfile.mkdtemp(prefix='anki_import_')
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                # Find the database file
                for db_name in self.DB_FILENAMES:
                    if db_name in zf.namelist():
                        zf.extract(db_name, self._temp_dir)
                        self._db_path = os.path.join(self._temp_dir, db_name)
                        return self._db_path
                
                # Check for any .anki2 file
                for name in zf.namelist():
                    if name.endswith('.anki2') or name.endswith('.anki21'):
                        zf.extract(name, self._temp_dir)
                        self._db_path = os.path.join(self._temp_dir, name)
                        return self._db_path
                
                raise AnkiDatabaseError("No Anki database found in package", str(self.file_path))
                
        except zipfile.BadZipFile:
            raise AnkiDatabaseError("Invalid or corrupted Anki package", str(self.file_path))
    
    def detect_settings(self) -> dict:
        """Detect package settings and structure."""
        if not self._db_path:
            self._extract_database()
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        try:
            # Get deck information
            cursor.execute("SELECT decks FROM col")
            row = cursor.fetchone()
            decks = {}
            if row and row[0]:
                try:
                    decks = json.loads(row[0])
                except json.JSONDecodeError:
                    pass
            
            # Get model/notetype information
            cursor.execute("SELECT models FROM col")
            row = cursor.fetchone()
            models = {}
            if row and row[0]:
                try:
                    models = json.loads(row[0])
                except json.JSONDecodeError:
                    pass
            
            # Count notes and cards
            cursor.execute("SELECT COUNT(*) FROM notes")
            note_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cards")
            card_count = cursor.fetchone()[0]
            
            self.settings = {
                'decks': {str(k): v.get('name', 'Unknown') for k, v in decks.items()},
                'models': {str(k): v.get('name', 'Unknown') for k, v in models.items()},
                'note_count': note_count,
                'card_count': card_count,
                'db_path': self._db_path
            }
            
        finally:
            conn.close()
        
        return self.settings
    
    def get_decks(self) -> Dict[str, str]:
        """Get dictionary of deck IDs to deck names."""
        if not self.settings:
            self.detect_settings()
        return self.settings.get('decks', {})
    
    def parse(self, deck_filter: str = None) -> ImportResult:
        """
        Parse the Anki package and return flashcards.
        
        Args:
            deck_filter: Optional deck name to filter by
        """
        result = ImportResult(source_file=str(self.file_path))
        
        if not self._db_path:
            self._extract_database()
        
        if not self.settings:
            self.detect_settings()
        
        result.deck_detected = bool(self.settings.get('decks'))
        
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()
        
        try:
            # Get deck ID to name mapping
            deck_map = self.settings.get('decks', {})
            
            # Get model field names
            model_fields = self._get_model_fields(cursor)
            
            # Query notes with their card's deck information
            query = """
                SELECT DISTINCT 
                    n.id,
                    n.mid,
                    n.flds,
                    n.tags,
                    c.did
                FROM notes n
                JOIN cards c ON c.nid = n.id
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                note_id, model_id, fields_str, tags_str, deck_id = row
                
                # Get deck name
                deck_name = deck_map.get(str(deck_id), 'Default')
                
                # Filter by deck if specified
                if deck_filter and deck_name.lower() != deck_filter.lower():
                    continue
                
                # Parse the note
                card = self._parse_note(
                    note_id=note_id,
                    model_id=model_id,
                    fields_str=fields_str,
                    tags_str=tags_str,
                    deck_name=deck_name,
                    model_fields=model_fields,
                    result=result
                )
                
                if card:
                    result.add_card(card)
            
        except sqlite3.Error as e:
            raise AnkiDatabaseError(f"Database error: {e}", self._db_path)
        finally:
            conn.close()
        
        if not result.cards:
            result.add_error("No valid cards found in package")
        
        return result
    
    def _get_model_fields(self, cursor) -> Dict[str, List[str]]:
        """Get field names for each model/notetype."""
        cursor.execute("SELECT models FROM col")
        row = cursor.fetchone()
        
        model_fields = {}
        if row and row[0]:
            try:
                models = json.loads(row[0])
                for mid, model in models.items():
                    fields = model.get('flds', [])
                    field_names = [f.get('name', f'Field{i}') for i, f in enumerate(fields)]
                    model_fields[str(mid)] = field_names
            except json.JSONDecodeError:
                pass
        
        return model_fields
    
    def _parse_note(
        self,
        note_id: int,
        model_id: int,
        fields_str: str,
        tags_str: str,
        deck_name: str,
        model_fields: Dict[str, List[str]],
        result: ImportResult
    ) -> Optional[Flashcard]:
        """Parse a single note into a Flashcard."""
        
        # Anki uses \x1f (unit separator) to separate fields
        fields = fields_str.split('\x1f')
        
        if len(fields) < 2:
            result.add_error(f"Note {note_id}: Not enough fields")
            return None
        
        # First field is typically front, second is back
        front = fields[0].strip()
        back = fields[1].strip() if len(fields) > 1 else ''
        
        # Check for HTML and optionally strip it for validation
        has_html = CardValidator.contains_html(front) or CardValidator.contains_html(back)
        
        # Validate content (use stripped version for validation)
        front_clean = CardValidator.strip_html(front) if has_html else front
        back_clean = CardValidator.strip_html(back) if has_html else back
        
        is_valid, error = CardValidator.validate_content(front_clean)
        if not is_valid:
            result.add_error(f"Note {note_id}: Front - {error}")
            return None
        
        is_valid, error = CardValidator.validate_content(back_clean)
        if not is_valid:
            result.add_error(f"Note {note_id}: Back - {error}")
            return None
        
        # Parse tags
        tags = []
        if tags_str:
            tags = [t.strip() for t in tags_str.split() if t.strip()]
        
        # Detect card type
        card_type = CardType.CLOZE if CardValidator.is_cloze_card(front) else CardType.BASIC
        
        # Extra fields (if any)
        extra = None
        if len(fields) > 2:
            extra = '\n'.join(f.strip() for f in fields[2:] if f.strip())
        
        return Flashcard(
            front=front,
            back=back,
            deck_name=deck_name,
            tags=tags,
            card_type=card_type,
            extra=extra,
            source_file=str(self.file_path),
            html_enabled=has_html
        )


# Register the parser
ParserFactory.register('.apkg', ApkgParser)
ParserFactory.register('.colpkg', ApkgParser)

