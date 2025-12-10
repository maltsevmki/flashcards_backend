"""Schemas for flashcard import endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CardImportSchema(BaseModel):
    """Schema for an imported flashcard."""
    front: str
    back: str
    deck_name: Optional[str] = None
    tags: List[str] = []
    card_type: str = "basic"
    extra: Optional[str] = None
    html_enabled: bool = False
    front_preview: Optional[str] = None
    back_preview: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "front": "What is Python?",
                "back": "A high-level programming language",
                "deck_name": "Programming",
                "tags": ["python", "basics"],
                "card_type": "basic",
                "html_enabled": False
            }
        }


class ImportOptionsSchema(BaseModel):
    """Options for import operation."""
    default_deck: Optional[str] = Field(None, description="Default deck for cards without deck info")
    auto_assign_decks: bool = Field(False, description="Use AI to suggest deck assignments")
    strip_html: bool = Field(False, description="Remove HTML tags from content")
    deck_filter: Optional[str] = Field(None, description="Only import from this deck (APKG only)")


class ImportSummarySchema(BaseModel):
    """Summary of import operation."""
    total_imported: int
    total_skipped: int
    success_rate: float
    deck_detected: bool


class ImportStatisticsSchema(BaseModel):
    """Statistics about imported cards."""
    deck_distribution: Dict[str, int]
    top_tags: Dict[str, int]
    cards_with_html: int
    cards_with_cloze: int


class ImportResultSchema(BaseModel):
    """Complete result of an import operation."""
    success: bool
    summary: ImportSummarySchema
    cards: List[CardImportSchema]
    statistics: ImportStatisticsSchema
    available_decks: Optional[List[str]] = None
    warnings: List[str] = []
    errors: List[str] = []


class FilePreviewSchema(BaseModel):
    """Preview information about a file."""
    filename: str
    format: str
    settings: Dict[str, Any]
    available_decks: Optional[List[str]] = None
    total_cards: int
    sample_cards: List[Dict[str, Any]]
    has_deck_info: bool


class ValidationResultSchema(BaseModel):
    """Result of file validation."""
    valid: bool
    filename: str
    format: Optional[str]
    total_cards: int
    issues: List[str]
    can_import: bool

