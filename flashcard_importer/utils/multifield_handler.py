from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FieldMapping:
    """Defines how columns/fields map to flashcard properties."""
    front: int = 0
    back: int = 1
    deck: Optional[int] = None
    tags: Optional[int] = None
    extra: Optional[int] = None
    hint: Optional[int] = None
    
    def get_required_columns(self) -> int:
        """Get minimum number of columns required."""
        return max(self.front, self.back) + 1
    
    def to_dict(self) -> Dict:
        return {
            'front': self.front,
            'back': self.back,
            'deck': self.deck,
            'tags': self.tags,
            'extra': self.extra,
            'hint': self.hint
        }


class MultiFieldHandler:
    """Handle multi-field notes (front, back, extra, hint, etc.)."""
    
    # Common field name patterns for auto-detection
    FIELD_PATTERNS = {
        'front': ['front', 'question', 'q', 'term', 'word', 'prompt', 'cue'],
        'back': ['back', 'answer', 'a', 'definition', 'meaning', 'response'],
        'extra': ['extra', 'notes', 'additional', 'context', 'explanation', 'info'],
        'hint': ['hint', 'clue', 'help', 'tip'],
        'deck': ['deck', 'category', 'group', 'collection', 'folder', 'chapter'],
        'tags': ['tags', 'tag', 'labels', 'keywords', 'topics']
    }
    
    @classmethod
    def detect_field_mapping(cls, headers: List[str]) -> FieldMapping:
        """Auto-detect field mapping from column headers."""
        mapping = FieldMapping()
        headers_lower = [h.lower().strip() if h else '' for h in headers]
        
        for i, header in enumerate(headers_lower):
            for field_type, patterns in cls.FIELD_PATTERNS.items():
                if header in patterns:
                    setattr(mapping, field_type, i)
                    break
        
        return mapping
    
    @classmethod
    def parse_row_with_mapping(cls, row: List, mapping: FieldMapping) -> Dict:
        """Parse a row using the specified field mapping."""
        result = {
            'front': '',
            'back': '',
            'deck': None,
            'tags': [],
            'extra': None,
            'hint': None
        }
        
        if len(row) > mapping.front:
            result['front'] = str(row[mapping.front]).strip() if row[mapping.front] else ''
        
        if len(row) > mapping.back:
            result['back'] = str(row[mapping.back]).strip() if row[mapping.back] else ''
        
        if mapping.deck is not None and len(row) > mapping.deck:
            val = row[mapping.deck]
            result['deck'] = str(val).strip() if val else None
        
        if mapping.tags is not None and len(row) > mapping.tags:
            val = row[mapping.tags]
            if val:
                tag_str = str(val).strip()
                if ',' in tag_str:
                    result['tags'] = [t.strip() for t in tag_str.split(',') if t.strip()]
                else:
                    result['tags'] = tag_str.split()
        
        if mapping.extra is not None and len(row) > mapping.extra:
            val = row[mapping.extra]
            result['extra'] = str(val).strip() if val else None
        
        if mapping.hint is not None and len(row) > mapping.hint:
            val = row[mapping.hint]
            result['hint'] = str(val).strip() if val else None
        
        return result
    
    @classmethod
    def merge_extra_fields(cls, fields: List[str], separator: str = '\n') -> Optional[str]:
        """Merge multiple extra fields into one string."""
        non_empty = [f.strip() for f in fields if f and f.strip()]
        if non_empty:
            return separator.join(non_empty)
        return None
    
    @classmethod
    def split_combined_field(cls, content: str, delimiter: str = '|') -> List[str]:
        """Split a combined field into multiple parts."""
        return [part.strip() for part in content.split(delimiter) if part.strip()]
    
    @classmethod
    def validate_mapping(cls, mapping: FieldMapping, column_count: int) -> Tuple[bool, List[str]]:
        """Validate that the mapping is valid for the given column count."""
        errors = []
        
        if mapping.front >= column_count:
            errors.append(f"Front column index {mapping.front} exceeds available columns ({column_count})")
        
        if mapping.back >= column_count:
            errors.append(f"Back column index {mapping.back} exceeds available columns ({column_count})")
        
        if mapping.front == mapping.back:
            errors.append("Front and back columns cannot be the same")
        
        return len(errors) == 0, errors

