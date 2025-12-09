"""
Integration tests for Deck API endpoints.
Tests basic endpoint availability and authentication.
Note: Full integration tests require proper database setup.
"""
import pytest


class TestDeckEndpointsAuthentication:
    """Tests for API authentication on deck endpoints."""

    @pytest.mark.anyio
    async def test_list_decks_without_api_key(self, async_client):
        """Test that list decks requires API key."""
        response = await async_client.get("/flashcards/decks/list")
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_list_decks_with_invalid_api_key(self, async_client, invalid_api_key_headers):
        """Test that invalid API key is rejected."""
        response = await async_client.get(
            "/flashcards/decks/list",
            headers=invalid_api_key_headers
        )
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_get_deck_without_api_key(self, async_client):
        """Test that get deck requires API key."""
        response = await async_client.get(
            "/flashcards/decks/get",
            params={"deck_id": 1}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_create_deck_without_api_key(self, async_client):
        """Test that create deck requires API key."""
        response = await async_client.post(
            "/flashcards/decks/create",
            params={"name": "New Deck"}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_update_deck_without_api_key(self, async_client):
        """Test that update deck requires API key."""
        response = await async_client.put(
            "/flashcards/decks/update",
            params={"deck_id": 1, "name": "Updated"}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_delete_deck_without_api_key(self, async_client):
        """Test that delete deck requires API key."""
        response = await async_client.delete(
            "/flashcards/decks/delete",
            params={"deck_id": 1}
        )
        assert response.status_code in [401, 403, 422]


class TestDeckEndpointsExist:
    """Tests that deck endpoints are properly mounted."""

    @pytest.mark.anyio
    async def test_decks_list_endpoint_exists(self, async_client):
        """Test that decks list endpoint exists."""
        response = await async_client.get("/flashcards/decks/list")
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_decks_get_endpoint_exists(self, async_client):
        """Test that decks get endpoint exists."""
        response = await async_client.get(
            "/flashcards/decks/get",
            params={"deck_id": 1}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_decks_create_endpoint_exists(self, async_client):
        """Test that decks create endpoint exists."""
        response = await async_client.post(
            "/flashcards/decks/create",
            params={"name": "Test Deck"}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_decks_update_endpoint_exists(self, async_client):
        """Test that decks update endpoint exists."""
        response = await async_client.put(
            "/flashcards/decks/update",
            params={"deck_id": 1, "name": "Updated"}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_decks_delete_endpoint_exists(self, async_client):
        """Test that decks delete endpoint exists."""
        response = await async_client.delete(
            "/flashcards/decks/delete",
            params={"deck_id": 1}
        )
        assert response.status_code != 404
