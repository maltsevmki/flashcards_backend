"""
Unit tests for the Card Service.
Tests all card-related CRUD operations and business logic.
"""
import pytest
from sqlmodel import select

from app.api.routers.flashcards.service import Service
from app.schemas.flashcards.input.card import (
    FlashcardCreateInput,
    FlashcardGetInput,
    FlashcardUpdateInput,
    FlashcardDeleteInput,
    FlashcardListInput,
    FlashcardReviewInput,
    FlashcardSearchInput
)
from app.models.flashcards.card import Card, CardTypeEnum, QueueTypeEnum
from app.models.flashcards.note import Note


class TestCardCreate:
    """Tests for card creation functionality."""

    @pytest.mark.anyio
    async def test_create_card_success(self, seeded_session):
        """Test successful card creation with valid data."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="What is the capital of France?",
            back="Paris",
            tags="geography europe"
        )
        
        result = await Service.create_card(seeded_session, data)
        
        assert result.card_id is not None
        assert result.note_id is not None
        assert result.deck == "Test Deck"
        assert result.front == "What is the capital of France?"
        assert result.back == "Paris"
        assert "geography europe" in result.tags

    @pytest.mark.anyio
    async def test_create_card_without_tags(self, seeded_session):
        """Test card creation without tags."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="Question without tags",
            back="Answer without tags"
        )
        
        result = await Service.create_card(seeded_session, data)
        
        assert result.card_id is not None
        assert result.tags == ""

    @pytest.mark.anyio
    async def test_create_card_nonexistent_deck(self, seeded_session):
        """Test card creation with non-existent deck raises error."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="NonExistent Deck",
            front="Question",
            back="Answer"
        )
        
        with pytest.raises(ValueError, match="Deck with name NonExistent Deck not found"):
            await Service.create_card(seeded_session, data)

    @pytest.mark.anyio
    async def test_create_card_nonexistent_notetype(self, seeded_session):
        """Test card creation with non-existent notetype raises error."""
        data = FlashcardCreateInput(
            type_name="NonExistent Type",
            deck_name="Test Deck",
            front="Question",
            back="Answer"
        )
        
        with pytest.raises(ValueError, match="No notetype found"):
            await Service.create_card(seeded_session, data)

    @pytest.mark.anyio
    async def test_create_duplicate_card(self, seeded_session):
        """Test creating duplicate card with same front raises error."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="Unique Question",
            back="Answer 1"
        )
        
        # Create first card
        await Service.create_card(seeded_session, data)
        
        # Try to create duplicate
        data2 = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="Unique Question",  # Same front
            back="Different Answer"
        )
        
        with pytest.raises(ValueError, match="Note with same sort field already exists"):
            await Service.create_card(seeded_session, data2)

    @pytest.mark.anyio
    @pytest.mark.skip(reason="SQLite integer overflow with current timestamps")
    async def test_create_card_sets_correct_initial_values(self, seeded_session):
        """Test that new cards have correct initial scheduling values."""
        data = FlashcardCreateInput(
            type_name="Basic",
            deck_name="Test Deck",
            front="New Card Question",
            back="New Card Answer"
        )
        
        result = await Service.create_card(seeded_session, data)
        
        # Verify card was created with NEW type and queue
        card = (await seeded_session.exec(
            select(Card).where(Card.id == result.card_id)
        )).first()
        
        assert card is not None
        assert card.type_id == CardTypeEnum.NEW.value
        assert card.queue_id == QueueTypeEnum.NEW.value
        assert card.ivl == 0
        assert card.factor == 2500
        assert card.reps == 0
        assert card.lapses == 0


class TestCardGet:
    """Tests for getting individual cards."""

    @pytest.mark.anyio
    async def test_get_card_success(self, seeded_session_with_cards):
        """Test getting an existing card."""
        data = FlashcardGetInput(card_id=1)
        
        result = await Service.get_card(seeded_session_with_cards, data)
        
        assert result.card_id == 1
        assert result.front == "What is Python?"
        assert result.back == "A programming language"
        assert result.deck == "Test Deck"

    @pytest.mark.anyio
    async def test_get_card_not_found(self, seeded_session):
        """Test getting non-existent card raises error."""
        data = FlashcardGetInput(card_id=99999)
        
        with pytest.raises(ValueError, match="Card with id 99999 not found"):
            await Service.get_card(seeded_session, data)

    @pytest.mark.anyio
    async def test_get_card_contains_all_fields(self, seeded_session_with_cards):
        """Test that get_card returns all expected fields."""
        data = FlashcardGetInput(card_id=1)
        
        result = await Service.get_card(seeded_session_with_cards, data)
        
        # Verify all fields are present
        assert hasattr(result, 'card_id')
        assert hasattr(result, 'note_id')
        assert hasattr(result, 'deck')
        assert hasattr(result, 'ord')
        assert hasattr(result, 'front')
        assert hasattr(result, 'back')
        assert hasattr(result, 'tags')
        assert hasattr(result, 'type_id')
        assert hasattr(result, 'queue_id')
        assert hasattr(result, 'due')
        assert hasattr(result, 'ivl')
        assert hasattr(result, 'factor')
        assert hasattr(result, 'reps')
        assert hasattr(result, 'lapses')
        assert hasattr(result, 'created_at')


class TestCardList:
    """Tests for listing cards."""

    @pytest.mark.anyio
    async def test_list_all_cards(self, seeded_session_with_cards):
        """Test listing all cards without filters."""
        data = FlashcardListInput()
        
        result = await Service.list_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 5

    @pytest.mark.anyio
    async def test_list_cards_by_deck_name(self, seeded_session_with_cards):
        """Test filtering cards by deck name."""
        data = FlashcardListInput(deck_name="Test Deck")
        
        result = await Service.list_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 5
        assert all(card.deck == "Test Deck" for card in result.cards)

    @pytest.mark.anyio
    async def test_list_cards_by_type(self, seeded_session_with_cards):
        """Test filtering cards by type_id."""
        data = FlashcardListInput(type_id=CardTypeEnum.NEW.value)
        
        result = await Service.list_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 5
        assert all(card.type_id == CardTypeEnum.NEW.value for card in result.cards)

    @pytest.mark.anyio
    async def test_list_cards_pagination_limit(self, seeded_session_with_cards):
        """Test pagination with limit."""
        data = FlashcardListInput(limit=2)
        
        result = await Service.list_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 2

    @pytest.mark.anyio
    async def test_list_cards_pagination_offset(self, seeded_session_with_cards):
        """Test pagination with offset."""
        data = FlashcardListInput(limit=2, offset=3)
        
        result = await Service.list_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 2

    @pytest.mark.anyio
    async def test_list_cards_nonexistent_deck(self, seeded_session_with_cards):
        """Test listing cards from non-existent deck returns empty list."""
        data = FlashcardListInput(deck_name="NonExistent Deck")
        
        result = await Service.list_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 0

    @pytest.mark.anyio
    async def test_list_cards_empty_database(self, seeded_session):
        """Test listing cards when no cards exist."""
        data = FlashcardListInput()
        
        result = await Service.list_cards(seeded_session, data)
        
        assert len(result.cards) == 0


class TestCardUpdate:
    """Tests for updating cards."""

    @pytest.mark.anyio
    async def test_update_card_front(self, seeded_session_with_cards):
        """Test updating card front text."""
        data = FlashcardUpdateInput(
            card_id=1,
            front="Updated Question"
        )
        
        result = await Service.update_card(seeded_session_with_cards, data)
        
        assert result.card_id == 1
        assert result.front == "Updated Question"
        assert result.back == "A programming language"  # Unchanged
        assert "updated successfully" in result.message.lower()

    @pytest.mark.anyio
    @pytest.mark.skip(reason="SQLite integer overflow with current timestamps")
    async def test_update_card_back(self, seeded_session_with_cards):
        """Test updating card back text."""
        data = FlashcardUpdateInput(
            card_id=1,
            back="Updated Answer"
        )
        
        result = await Service.update_card(seeded_session_with_cards, data)
        
        assert result.front == "What is Python?"  # Unchanged
        assert result.back == "Updated Answer"

    @pytest.mark.anyio
    @pytest.mark.skip(reason="SQLite integer overflow with current timestamps")
    async def test_update_card_tags(self, seeded_session_with_cards):
        """Test updating card tags."""
        data = FlashcardUpdateInput(
            card_id=1,
            tags="new-tag updated"
        )
        
        result = await Service.update_card(seeded_session_with_cards, data)
        
        assert result.tags == "new-tag updated"

    @pytest.mark.anyio
    async def test_update_card_multiple_fields(self, seeded_session_with_cards):
        """Test updating multiple fields at once."""
        data = FlashcardUpdateInput(
            card_id=1,
            front="New Front",
            back="New Back",
            tags="new-tags"
        )
        
        result = await Service.update_card(seeded_session_with_cards, data)
        
        assert result.front == "New Front"
        assert result.back == "New Back"
        assert result.tags == "new-tags"

    @pytest.mark.anyio
    async def test_update_card_not_found(self, seeded_session):
        """Test updating non-existent card raises error."""
        data = FlashcardUpdateInput(
            card_id=99999,
            front="Updated"
        )
        
        with pytest.raises(ValueError, match="Card with id 99999 not found"):
            await Service.update_card(seeded_session, data)

    @pytest.mark.anyio
    async def test_update_card_no_fields(self, seeded_session_with_cards):
        """Test updating without any fields raises error."""
        data = FlashcardUpdateInput(card_id=1)
        
        with pytest.raises(ValueError, match="At least one field"):
            await Service.update_card(seeded_session_with_cards, data)


class TestCardDelete:
    """Tests for deleting cards."""

    @pytest.mark.anyio
    async def test_delete_card_success(self, seeded_session_with_cards):
        """Test successful card deletion."""
        data = FlashcardDeleteInput(card_id=1)
        
        result = await Service.delete_card(seeded_session_with_cards, data)
        
        assert result.card_id == 1
        assert "deleted successfully" in result.message.lower()
        
        # Verify card is actually deleted
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        assert card is None

    @pytest.mark.anyio
    async def test_delete_card_also_deletes_orphan_note(self, seeded_session_with_cards):
        """Test that deleting the only card of a note also deletes the note."""
        data = FlashcardDeleteInput(card_id=1)
        note_id = 1
        
        await Service.delete_card(seeded_session_with_cards, data)
        
        # Verify note is also deleted
        note = (await seeded_session_with_cards.exec(
            select(Note).where(Note.id == note_id)
        )).first()
        assert note is None

    @pytest.mark.anyio
    async def test_delete_card_not_found(self, seeded_session):
        """Test deleting non-existent card raises error."""
        data = FlashcardDeleteInput(card_id=99999)
        
        with pytest.raises(ValueError, match="Card with id 99999 not found"):
            await Service.delete_card(seeded_session, data)


class TestCardReview:
    """Tests for card review functionality (spaced repetition logic)."""

    @pytest.mark.anyio
    async def test_review_new_card_transitions_to_learning(self, seeded_session_with_cards):
        """Test that reviewing a new card transitions it to learning."""
        data = FlashcardReviewInput(
            card_id=1,
            ease=3,  # Good
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        assert result.card_id == 1
        assert result.type_id == CardTypeEnum.LEARNING.value
        assert result.queue_id == QueueTypeEnum.LEARNING.value
        assert result.reps == 1

    @pytest.mark.anyio
    async def test_review_learning_card_transitions_to_review(self, seeded_session_with_cards):
        """Test that reviewing a learning card transitions it to review."""
        # First, make the card a learning card
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        card.type_id = CardTypeEnum.LEARNING.value
        card.queue_id = QueueTypeEnum.LEARNING.value
        await seeded_session_with_cards.commit()
        
        data = FlashcardReviewInput(
            card_id=1,
            ease=3,
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        assert result.type_id == CardTypeEnum.REVIEW.value
        assert result.queue_id == QueueTypeEnum.REVIEW.value
        assert result.new_ivl == 1

    @pytest.mark.anyio
    async def test_review_card_ease_again_increases_lapses(self, seeded_session_with_cards):
        """Test that reviewing with ease=1 (Again) increases lapses."""
        # Make card a review card
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        card.type_id = CardTypeEnum.REVIEW.value
        card.queue_id = QueueTypeEnum.REVIEW.value
        card.ivl = 10
        await seeded_session_with_cards.commit()
        
        data = FlashcardReviewInput(
            card_id=1,
            ease=1,  # Again
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        assert result.lapses == 1
        assert result.new_ivl == 1  # Reset to 1 day

    @pytest.mark.anyio
    async def test_review_card_ease_hard_decreases_factor(self, seeded_session_with_cards):
        """Test that reviewing with ease=2 (Hard) decreases factor."""
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        card.type_id = CardTypeEnum.REVIEW.value
        card.queue_id = QueueTypeEnum.REVIEW.value
        card.ivl = 10
        card.factor = 2500
        await seeded_session_with_cards.commit()
        
        data = FlashcardReviewInput(
            card_id=1,
            ease=2,  # Hard
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        assert result.new_factor == 2350  # 2500 - 150

    @pytest.mark.anyio
    async def test_review_card_ease_good_normal_progression(self, seeded_session_with_cards):
        """Test that reviewing with ease=3 (Good) follows normal progression."""
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        card.type_id = CardTypeEnum.REVIEW.value
        card.queue_id = QueueTypeEnum.REVIEW.value
        card.ivl = 10
        card.factor = 2500
        await seeded_session_with_cards.commit()
        
        data = FlashcardReviewInput(
            card_id=1,
            ease=3,  # Good
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        # ivl * factor / 1000 = 10 * 2500 / 1000 = 25
        assert result.new_ivl == 25

    @pytest.mark.anyio
    async def test_review_card_ease_easy_bonus(self, seeded_session_with_cards):
        """Test that reviewing with ease=4 (Easy) gives bonus interval."""
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        card.type_id = CardTypeEnum.REVIEW.value
        card.queue_id = QueueTypeEnum.REVIEW.value
        card.ivl = 10
        card.factor = 2500
        await seeded_session_with_cards.commit()
        
        data = FlashcardReviewInput(
            card_id=1,
            ease=4,  # Easy
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        # ivl * factor / 1000 * 1.3 = 10 * 2500 / 1000 * 1.3 = 32
        assert result.new_ivl == 32

    @pytest.mark.anyio
    async def test_review_card_not_found(self, seeded_session):
        """Test reviewing non-existent card raises error."""
        data = FlashcardReviewInput(
            card_id=99999,
            ease=3,
            review_time_ms=5000
        )
        
        with pytest.raises(ValueError, match="Card not found"):
            await Service.review_card(seeded_session, data)

    @pytest.mark.anyio
    async def test_review_creates_revlog_entry(self, seeded_session_with_cards):
        """Test that review creates a review log entry."""
        data = FlashcardReviewInput(
            card_id=1,
            ease=3,
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        assert result.revlog_id is not None

    @pytest.mark.anyio
    async def test_review_factor_has_minimum(self, seeded_session_with_cards):
        """Test that factor never goes below minimum (1300)."""
        card = (await seeded_session_with_cards.exec(
            select(Card).where(Card.id == 1)
        )).first()
        card.type_id = CardTypeEnum.REVIEW.value
        card.queue_id = QueueTypeEnum.REVIEW.value
        card.ivl = 10
        card.factor = 1300  # Already at minimum
        await seeded_session_with_cards.commit()
        
        data = FlashcardReviewInput(
            card_id=1,
            ease=1,  # Again - would normally decrease factor by 200
            review_time_ms=5000
        )
        
        result = await Service.review_card(seeded_session_with_cards, data)
        
        assert result.new_factor == 1300  # Stays at minimum


class TestCardSearch:
    """Tests for card search functionality."""

    @pytest.mark.anyio
    async def test_search_cards_by_content(self, seeded_session_with_cards):
        """Test searching cards by content."""
        data = FlashcardSearchInput(query="Python")
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        # Should find cards mentioning Python
        assert len(result.cards) >= 1
        assert any("Python" in card.front or "Python" in card.back 
                   for card in result.cards)

    @pytest.mark.anyio
    async def test_search_cards_case_insensitive(self, seeded_session_with_cards):
        """Test that search is case insensitive."""
        data = FlashcardSearchInput(query="python")
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) >= 1

    @pytest.mark.anyio
    async def test_search_cards_with_deck_filter(self, seeded_session_with_cards):
        """Test searching with deck filter."""
        data = FlashcardSearchInput(
            query="Python",
            deck_name="Test Deck"
        )
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        assert all(card.deck == "Test Deck" for card in result.cards)

    @pytest.mark.anyio
    async def test_search_cards_with_tags_filter(self, seeded_session_with_cards):
        """Test searching with tags filter."""
        data = FlashcardSearchInput(
            query="What",
            tags="testing"
        )
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) >= 1
        assert any("testing" in card.tags for card in result.cards)

    @pytest.mark.anyio
    async def test_search_cards_with_type_filter(self, seeded_session_with_cards):
        """Test searching with type filter."""
        data = FlashcardSearchInput(
            query="What",
            type_id=CardTypeEnum.NEW.value
        )
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        assert all(card.type_id == CardTypeEnum.NEW.value for card in result.cards)

    @pytest.mark.anyio
    async def test_search_cards_no_results(self, seeded_session_with_cards):
        """Test search with no matching results."""
        data = FlashcardSearchInput(query="xyznonexistent123")
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) == 0

    @pytest.mark.anyio
    async def test_search_cards_pagination(self, seeded_session_with_cards):
        """Test search pagination."""
        data = FlashcardSearchInput(
            query="What",
            limit=2,
            offset=0
        )
        
        result = await Service.search_cards(seeded_session_with_cards, data)
        
        assert len(result.cards) <= 2


