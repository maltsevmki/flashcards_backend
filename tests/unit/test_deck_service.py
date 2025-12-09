"""
Unit tests for the Deck Service.
Tests all deck-related CRUD operations.
"""
import pytest
from sqlmodel import select

from app.api.routers.flashcards.service import Service
from app.schemas.flashcards.input.deck import (
    DeckCreateInput,
    DeckGetInput,
    DeckUpdateInput,
    DeckDeleteInput,
    DeckListInput
)
from app.models.flashcards.deck import Deck
import time


class TestDeckCreate:
    """Tests for deck creation functionality."""

    @pytest.mark.anyio
    async def test_create_deck_success(self, seeded_session):
        """Test successful deck creation."""
        data = DeckCreateInput(name="New Test Deck")
        
        result = await Service.create_deck(seeded_session, data)
        
        assert result.deck_id is not None
        assert result.name == "New Test Deck"

    @pytest.mark.anyio
    async def test_create_deck_duplicate_name(self, seeded_session):
        """Test creating deck with duplicate name raises error."""
        # "Test Deck" already exists in seeded_session
        data = DeckCreateInput(name="Test Deck")
        
        with pytest.raises(ValueError, match="already exists"):
            await Service.create_deck(seeded_session, data)

    @pytest.mark.anyio
    async def test_create_deck_special_characters(self, seeded_session):
        """Test creating deck with special characters in name."""
        data = DeckCreateInput(name="Deck::SubDeck::Level3")
        
        result = await Service.create_deck(seeded_session, data)
        
        assert result.name == "Deck::SubDeck::Level3"

    @pytest.mark.anyio
    async def test_create_deck_unicode_name(self, seeded_session):
        """Test creating deck with unicode characters."""
        data = DeckCreateInput(name="日本語デッキ 🎴")
        
        result = await Service.create_deck(seeded_session, data)
        
        assert result.name == "日本語デッキ 🎴"

    @pytest.mark.anyio
    async def test_create_deck_sets_correct_metadata(self, seeded_session):
        """Test that created deck has correct metadata."""
        data = DeckCreateInput(name="Metadata Test Deck")
        
        result = await Service.create_deck(seeded_session, data)
        
        # Verify deck was created with proper metadata
        deck = (await seeded_session.exec(
            select(Deck).where(Deck.id == result.deck_id)
        )).first()
        
        assert deck is not None
        assert deck.collection_id == 1
        assert deck.config_id == 1
        assert deck.mtime_secs > 0


class TestDeckGet:
    """Tests for getting individual decks."""

    @pytest.mark.anyio
    async def test_get_deck_success(self, seeded_session):
        """Test getting an existing deck."""
        data = DeckGetInput(deck_id=1)
        
        result = await Service.get_deck(seeded_session, data)
        
        assert result.deck_id == 1
        assert result.name == "Test Deck"

    @pytest.mark.anyio
    async def test_get_deck_not_found(self, seeded_session):
        """Test getting non-existent deck raises error."""
        data = DeckGetInput(deck_id=99999)
        
        with pytest.raises(ValueError, match="Deck with id=99999 not found"):
            await Service.get_deck(seeded_session, data)

    @pytest.mark.anyio
    async def test_get_deck_with_card_count(self, seeded_session_with_cards):
        """Test that get_deck returns correct card count."""
        data = DeckGetInput(deck_id=1)
        
        result = await Service.get_deck(seeded_session_with_cards, data)
        
        assert result.cards == 5  # We seeded 5 cards

    @pytest.mark.anyio
    async def test_get_deck_empty_card_count(self, seeded_session):
        """Test that empty deck has zero card count."""
        data = DeckGetInput(deck_id=1)
        
        result = await Service.get_deck(seeded_session, data)
        
        assert result.cards == 0

    @pytest.mark.anyio
    async def test_get_deck_contains_all_fields(self, seeded_session):
        """Test that get_deck returns all expected fields."""
        data = DeckGetInput(deck_id=1)
        
        result = await Service.get_deck(seeded_session, data)
        
        assert hasattr(result, 'deck_id')
        assert hasattr(result, 'name')
        assert hasattr(result, 'cards')
        assert hasattr(result, 'collection_id')
        assert hasattr(result, 'config_id')
        assert hasattr(result, 'mtime_secs')


class TestDeckList:
    """Tests for listing decks."""

    @pytest.mark.anyio
    async def test_list_decks_success(self, seeded_session):
        """Test listing all decks."""
        data = DeckListInput()
        
        result = await Service.list_decks(seeded_session, data)
        
        assert len(result.decks) >= 1
        assert any(deck.name == "Test Deck" for deck in result.decks)

    @pytest.mark.anyio
    async def test_list_decks_pagination_limit(self, seeded_session):
        """Test pagination with limit."""
        # Create additional decks
        for i in range(5):
            deck = Deck(
                name=f"Extra Deck {i}",
                mtime_secs=int(time.time()),
                usn=0,
                collection_id=1,
                config_id=1
            )
            seeded_session.add(deck)
        await seeded_session.commit()
        
        data = DeckListInput(limit=3)
        
        result = await Service.list_decks(seeded_session, data)
        
        assert len(result.decks) == 3

    @pytest.mark.anyio
    async def test_list_decks_pagination_offset(self, seeded_session):
        """Test pagination with offset."""
        # Create additional decks
        for i in range(5):
            deck = Deck(
                name=f"Offset Deck {i}",
                mtime_secs=int(time.time()),
                usn=0,
                collection_id=1,
                config_id=1
            )
            seeded_session.add(deck)
        await seeded_session.commit()
        
        data = DeckListInput(limit=2, offset=2)
        
        result = await Service.list_decks(seeded_session, data)
        
        assert len(result.decks) == 2

    @pytest.mark.anyio
    async def test_list_decks_with_card_counts(self, seeded_session_with_cards):
        """Test that list_decks includes card counts."""
        data = DeckListInput()
        
        result = await Service.list_decks(seeded_session_with_cards, data)
        
        test_deck = next((d for d in result.decks if d.name == "Test Deck"), None)
        assert test_deck is not None
        assert test_deck.cards == 5


class TestDeckUpdate:
    """Tests for updating decks."""

    @pytest.mark.anyio
    async def test_update_deck_name(self, seeded_session):
        """Test updating deck name."""
        data = DeckUpdateInput(
            deck_id=1,
            new_name="Updated Deck Name"
        )
        
        result = await Service.update_deck(seeded_session, data)
        
        assert result.name == "Updated Deck Name"
        assert result.updated_name == "Updated Deck Name"
        assert "updated successfully" in result.message.lower()

    @pytest.mark.anyio
    async def test_update_deck_config(self, seeded_session):
        """Test updating deck config_id."""
        data = DeckUpdateInput(
            deck_id=1,
            config_id=1
        )
        
        result = await Service.update_deck(seeded_session, data)
        
        # Config was already 1, so updated_config_id should be None
        # (no actual change)
        assert result.updated_config_id is None

    @pytest.mark.anyio
    async def test_update_deck_not_found(self, seeded_session):
        """Test updating non-existent deck raises error."""
        data = DeckUpdateInput(
            deck_id=99999,
            new_name="New Name"
        )
        
        with pytest.raises(ValueError, match="Deck with id=99999 not found"):
            await Service.update_deck(seeded_session, data)

    @pytest.mark.anyio
    async def test_update_deck_updates_mtime(self, seeded_session):
        """Test that updating deck updates modification time."""
        original_deck = (await seeded_session.exec(
            select(Deck).where(Deck.id == 1)
        )).first()
        original_mtime = original_deck.mtime_secs
        
        # Wait a moment to ensure different timestamp
        import asyncio
        await asyncio.sleep(0.1)
        
        data = DeckUpdateInput(
            deck_id=1,
            new_name="Time Update Test"
        )
        
        result = await Service.update_deck(seeded_session, data)
        
        assert result.updated_at >= original_mtime


class TestDeckDelete:
    """Tests for deleting decks."""

    @pytest.mark.anyio
    async def test_delete_empty_deck(self, seeded_session):
        """Test deleting an empty deck."""
        # Create a new empty deck to delete
        new_deck = Deck(
            name="Deck To Delete",
            mtime_secs=int(time.time()),
            usn=0,
            collection_id=1,
            config_id=1
        )
        seeded_session.add(new_deck)
        await seeded_session.commit()
        await seeded_session.refresh(new_deck)
        
        data = DeckDeleteInput(deck_id=new_deck.id)
        
        result = await Service.delete_deck(seeded_session, data)
        
        assert result.name == "Deck To Delete"
        assert result.deleted_cards == 0
        assert result.deleted_notes == 0
        assert "deleted successfully" in result.message.lower()
        
        # Verify deck is actually deleted
        deck = (await seeded_session.exec(
            select(Deck).where(Deck.id == new_deck.id)
        )).first()
        assert deck is None

    @pytest.mark.anyio
    @pytest.mark.skip(reason="SQLite CASCADE delete issue in test environment")
    async def test_delete_deck_with_cards(self, seeded_session_with_cards):
        """Test deleting a deck with cards."""
        data = DeckDeleteInput(deck_id=1)
        
        result = await Service.delete_deck(seeded_session_with_cards, data)
        
        assert result.name == "Test Deck"
        assert result.deleted_cards == 5
        assert result.deleted_notes == 5  # Each card has its own note

    @pytest.mark.anyio
    async def test_delete_deck_not_found(self, seeded_session):
        """Test deleting non-existent deck raises error."""
        data = DeckDeleteInput(deck_id=99999)
        
        with pytest.raises(ValueError, match="Deck with id.*99999 not found"):
            await Service.delete_deck(seeded_session, data)

    @pytest.mark.anyio
    async def test_delete_deck_returns_deleted_at(self, seeded_session):
        """Test that delete returns deleted_at timestamp."""
        # Create a deck to delete
        new_deck = Deck(
            name="Timestamp Test Deck",
            mtime_secs=int(time.time()),
            usn=0,
            collection_id=1,
            config_id=1
        )
        seeded_session.add(new_deck)
        await seeded_session.commit()
        await seeded_session.refresh(new_deck)
        
        data = DeckDeleteInput(deck_id=new_deck.id)
        
        result = await Service.delete_deck(seeded_session, data)
        
        assert result.deleted_at > 0


class TestDeckEdgeCases:
    """Edge case tests for deck operations."""

    @pytest.mark.anyio
    async def test_deck_name_with_leading_trailing_spaces(self, seeded_session):
        """Test deck creation with spaces in name."""
        data = DeckCreateInput(name="  Spaced Deck  ")
        
        result = await Service.create_deck(seeded_session, data)
        
        # Name should be preserved as-is
        assert result.name == "  Spaced Deck  "

    @pytest.mark.anyio
    async def test_deck_empty_name(self, seeded_session):
        """Test deck creation with empty name."""
        data = DeckCreateInput(name="")
        
        # Should still create (validation is at API level)
        result = await Service.create_deck(seeded_session, data)
        
        assert result.name == ""

    @pytest.mark.anyio
    async def test_deck_very_long_name(self, seeded_session):
        """Test deck creation with very long name."""
        long_name = "A" * 1000
        data = DeckCreateInput(name=long_name)
        
        result = await Service.create_deck(seeded_session, data)
        
        assert result.name == long_name
        assert len(result.name) == 1000

    @pytest.mark.anyio
    async def test_multiple_decks_same_collection(self, seeded_session):
        """Test creating multiple decks in the same collection."""
        deck_names = ["Deck A", "Deck B", "Deck C"]
        
        for name in deck_names:
            data = DeckCreateInput(name=name)
            await Service.create_deck(seeded_session, data)
        
        data = DeckListInput()
        result = await Service.list_decks(seeded_session, data)
        
        # Should have original "Test Deck" plus 3 new ones
        assert len(result.decks) >= 4

