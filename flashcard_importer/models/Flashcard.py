"""
Flashcard data model for imported cards.
Uses dataclasses for clean, type-hinted data structures.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class CardType(Enum):
    """Type of flashcard."""
    BASIC = "basic"  # Simple front/back
    BASIC_REVERSED = "reversed"  # Creates both directions
    CLOZE = "cloze"  # Fill-in-the-blank style


@dataclass
class Flashcard:
    """
    Represents a single flashcard imported from external sources.

    Attributes:
        front: The question/prompt side of the card
        back: The answer side of the card
        deck_name: Name of the deck this card belongs to (optional)
        tags: List of tags associated with this card
        card_type: Type of card (basic, reversed, cloze)
        extra: Additional information/notes (optional)
        source_file: Original file this card was imported from
        html_enabled: Whether the content contains HTML formatting
        created_at: Timestamp when the card was created/imported
    """
    front: str
    back: str
    deck_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    card_type: CardType = CardType.BASIC
    extra: Optional[str] = None
    source_file: Optional[str] = None
    html_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and clean data after initialization."""
        # Strip whitespace from front and back
        self.front = self.front.strip()
        self.back = self.back.strip()

        # Clean deck name if provided
        if self.deck_name:
            self.deck_name = self.deck_name.strip()

        # Clean tags
        self.tags = [tag.strip() for tag in self.tags if tag.strip()]

    def is_valid(self) -> bool:
        """Check if the flashcard has minimum required content."""
        return bool(self.front) and bool(self.back)

    def to_dict(self) -> dict:
        """Convert flashcard to dictionary for JSON serialization."""
        return {
            "front": self.front,
            "back": self.back,
            "deck_name": self.deck_name,
            "tags": self.tags,
            "card_type": self.card_type.value,
            "extra": self.extra,
            "source_file": self.source_file,
            "html_enabled": self.html_enabled,
            "created_at": self.created_at.isoformat()
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        front_preview = self.front[:50] + "..." if len(self.front) > 50 else self.front
        return f"Flashcard(front='{front_preview}', deck='{self.deck_name}')"


@dataclass
class ImportResult:
    """
    Result of an import operation.

    Attributes:
        cards: Successfully imported flashcards
        skipped_count: Number of cards skipped due to errors
        errors: List of error messages for skipped cards
        source_file: The file that was imported
        deck_detected: Whether deck information was found in the file
    """
    cards: List[Flashcard] = field(default_factory=list)
    skipped_count: int = 0
    errors: List[str] = field(default_factory=list)
    source_file: Optional[str] = None
    deck_detected: bool = False

    @property
    def total_processed(self) -> int:
        """Total number of cards processed (success + skipped)."""
        return len(self.cards) + self.skipped_count

    @property
    def success_rate(self) -> float:
        """Percentage of successfully imported cards."""
        if self.total_processed == 0:
            return 0.0
        return len(self.cards) / self.total_processed * 100

    def add_card(self, card: Flashcard) -> None:
        """Add a successfully parsed card."""
        self.cards.append(card)

    def add_error(self, error_message: str) -> None:
        """Record a parsing error and increment skip count."""
        self.errors.append(error_message)
        self.skipped_count += 1

    def summary(self) -> str:
        """Generate a human-readable summary of the import."""
        return (
            f"Import Summary for '{self.source_file}':\n"
            f"  ✓ Imported: {len(self.cards)} cards\n"
            f"  ✗ Skipped: {self.skipped_count} cards\n"
            f"  Success Rate: {self.success_rate:.1f}%\n"
            f"  Deck Info Found: {'Yes' if self.deck_detected else 'No'}"
        )