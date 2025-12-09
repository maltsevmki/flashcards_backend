"""
Tests for input validation and edge cases.
"""
import pytest
from pydantic import ValidationError

from app.schemas.flashcards.input.card import (
    FlashcardCreateInput,
    FlashcardGetInput,
    FlashcardUpdateInput,
    FlashcardDeleteInput,
    FlashcardListInput,
    FlashcardReviewInput,
    FlashcardSearchInput
)
from app.schemas.flashcards.input.deck import (
    DeckCreateInput,
    DeckGetInput,
    DeckUpdateInput,
    DeckDeleteInput,
    DeckListInput
)


class TestCardInputValidation:
    """Tests for card input schema validation."""

    def test_flashcard_create_input_valid(self):
        """Test valid FlashcardCreateInput."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="Question",
            back="Answer",
            tags="tag1 tag2"
        )
        
        assert data.type_name == "Basic"
        assert data.deck_name == "Test Deck"
        assert data.front == "Question"
        assert data.back == "Answer"
        assert data.tags == "tag1 tag2"

    def test_flashcard_create_input_minimal(self):
        """Test FlashcardCreateInput with only required fields."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="Question",
            back="Answer"
        )
        
        assert data.tags == ""
        assert data.user_timezone_offset_minutes == 0

    def test_flashcard_create_input_missing_required(self):
        """Test FlashcardCreateInput without required fields raises error."""
        with pytest.raises(ValidationError):
            FlashcardCreateInput(
                type_name="Basic"
                # Missing deck_name, front, back
            )

    def test_flashcard_get_input_valid(self):
        """Test valid FlashcardGetInput."""
        data = FlashcardGetInput(card_id=1)
        
        assert data.card_id == 1

    def test_flashcard_get_input_missing_card_id(self):
        """Test FlashcardGetInput without card_id raises error."""
        with pytest.raises(ValidationError):
            FlashcardGetInput()

    def test_flashcard_update_input_valid(self):
        """Test valid FlashcardUpdateInput."""
        data = FlashcardUpdateInput(
            card_id=1,
            front="Updated Front",
            back="Updated Back",
            tags="new-tags"
        )
        
        assert data.card_id == 1
        assert data.front == "Updated Front"

    def test_flashcard_update_input_partial(self):
        """Test FlashcardUpdateInput with partial fields."""
        data = FlashcardUpdateInput(
            card_id=1,
            front="Only Front Updated"
        )
        
        assert data.front == "Only Front Updated"
        assert data.back is None
        assert data.tags is None

    def test_flashcard_delete_input_valid(self):
        """Test valid FlashcardDeleteInput."""
        data = FlashcardDeleteInput(card_id=1)
        
        assert data.card_id == 1

    def test_flashcard_list_input_defaults(self):
        """Test FlashcardListInput default values."""
        data = FlashcardListInput()
        
        assert data.deck_name is None
        assert data.type_id is None
        assert data.limit == 100
        assert data.offset == 0

    def test_flashcard_list_input_custom_pagination(self):
        """Test FlashcardListInput with custom pagination."""
        data = FlashcardListInput(limit=50, offset=25)
        
        assert data.limit == 50
        assert data.offset == 25

    def test_flashcard_review_input_valid(self):
        """Test valid FlashcardReviewInput."""
        data = FlashcardReviewInput(
            card_id=1,
            ease=3,
            review_time_ms=5000
        )
        
        assert data.card_id == 1
        assert data.ease == 3
        assert data.review_time_ms == 5000

    def test_flashcard_review_input_all_ease_values(self):
        """Test FlashcardReviewInput with all valid ease values."""
        for ease in [1, 2, 3, 4]:
            data = FlashcardReviewInput(
                card_id=1,
                ease=ease,
                review_time_ms=5000
            )
            assert data.ease == ease

    def test_flashcard_search_input_valid(self):
        """Test valid FlashcardSearchInput."""
        data = FlashcardSearchInput(
            query="python",
            deck_name="Test Deck",
            tags="programming",
            type_id=0,
            limit=50,
            offset=10
        )
        
        assert data.query == "python"
        assert data.deck_name == "Test Deck"
        assert data.tags == "programming"

    def test_flashcard_search_input_minimal(self):
        """Test FlashcardSearchInput with only query."""
        data = FlashcardSearchInput(query="search term")
        
        assert data.query == "search term"
        assert data.deck_name is None
        assert data.tags is None
        assert data.type_id is None


class TestDeckInputValidation:
    """Tests for deck input schema validation."""

    def test_deck_create_input_valid(self):
        """Test valid DeckCreateInput."""
        data = DeckCreateInput(name="My Deck")
        
        assert data.name == "My Deck"

    def test_deck_create_input_missing_name(self):
        """Test DeckCreateInput without name raises error."""
        with pytest.raises(ValidationError):
            DeckCreateInput()

    def test_deck_get_input_valid(self):
        """Test valid DeckGetInput."""
        data = DeckGetInput(deck_id=1)
        
        assert data.deck_id == 1

    def test_deck_update_input_valid(self):
        """Test valid DeckUpdateInput."""
        data = DeckUpdateInput(
            deck_id=1,
            new_name="New Name",
            config_id=2
        )
        
        assert data.deck_id == 1
        assert data.new_name == "New Name"
        assert data.config_id == 2

    def test_deck_update_input_partial(self):
        """Test DeckUpdateInput with only deck_id."""
        data = DeckUpdateInput(deck_id=1)
        
        assert data.deck_id == 1
        assert data.new_name is None
        assert data.config_id is None

    def test_deck_delete_input_valid(self):
        """Test valid DeckDeleteInput."""
        data = DeckDeleteInput(deck_id=1)
        
        assert data.deck_id == 1

    def test_deck_list_input_defaults(self):
        """Test DeckListInput default values."""
        data = DeckListInput()
        
        assert data.limit == 100
        assert data.offset == 0


class TestInputEdgeCases:
    """Tests for edge cases in input validation."""

    def test_empty_string_fields(self):
        """Test that empty strings are accepted where allowed."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test",
            front="",  # Empty front
            back=""    # Empty back
        )
        
        assert data.front == ""
        assert data.back == ""

    def test_very_long_strings(self):
        """Test very long string inputs."""
        long_string = "A" * 10000
        
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test",
            front=long_string,
            back=long_string
        )
        
        assert len(data.front) == 10000
        assert len(data.back) == 10000

    def test_unicode_characters(self):
        """Test unicode characters in inputs."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="日本語",
            front="什么是Python？",
            back="Python是一种编程语言 🐍"
        )
        
        assert data.deck_name == "日本語"
        assert "Python" in data.front
        assert "🐍" in data.back

    def test_special_characters(self):
        """Test special characters in inputs."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Deck::SubDeck",
            front="<script>alert('xss')</script>",
            back="'\"\\n\\t"
        )
        
        # Should accept special characters (escaping is handled elsewhere)
        assert "<script>" in data.front

    def test_whitespace_handling(self):
        """Test whitespace in inputs."""
        data = FlashcardCreateInput(
            type_name="  Basic  ",
            deck_name="  Test Deck  ",
            front="  Question with spaces  ",
            back="  Answer with spaces  "
        )
        
        # Whitespace should be preserved
        assert data.type_name == "  Basic  "

    def test_newlines_in_content(self):
        """Test newlines in card content."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test",
            front="Line 1\nLine 2\nLine 3",
            back="Answer\nWith\nNewlines"
        )
        
        assert "\n" in data.front
        assert data.front.count("\n") == 2

    def test_zero_values(self):
        """Test zero values in numeric fields."""
        data = FlashcardListInput(limit=0, offset=0)
        
        assert data.limit == 0
        assert data.offset == 0

    def test_large_numeric_values(self):
        """Test large numeric values."""
        data = FlashcardListInput(
            limit=1000000,
            offset=1000000
        )
        
        assert data.limit == 1000000
        assert data.offset == 1000000

    def test_negative_timezone_offset(self):
        """Test negative timezone offset."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test",
            front="Q",
            back="A",
            user_timezone_offset_minutes=-480  # UTC-8
        )
        
        assert data.user_timezone_offset_minutes == -480

    def test_positive_timezone_offset(self):
        """Test positive timezone offset."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test",
            front="Q",
            back="A",
            user_timezone_offset_minutes=330  # UTC+5:30
        )
        
        assert data.user_timezone_offset_minutes == 330

