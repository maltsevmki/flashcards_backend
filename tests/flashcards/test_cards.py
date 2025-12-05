"""
Integration tests for Card API endpoints.
Tests basic endpoint availability and authentication.
Note: Full integration tests require proper database setup.
"""
import pytest


class TestCardEndpointsAuthentication:
    """Tests for API authentication on card endpoints."""

    @pytest.mark.anyio
    async def test_list_cards_without_api_key(self, async_client):
        """Test that list cards requires API key."""
        response = await async_client.get("/flashcards/cards/list")
        # Without API key, should return auth error
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_list_cards_with_invalid_api_key(self, async_client, invalid_api_key_headers):
        """Test that invalid API key is rejected."""
        response = await async_client.get(
            "/flashcards/cards/list",
            headers=invalid_api_key_headers
        )
        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_get_card_without_api_key(self, async_client):
        """Test that get card requires API key."""
        response = await async_client.get(
            "/flashcards/cards/get",
            params={"card_id": 1}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_create_card_without_api_key(self, async_client):
        """Test that create card requires API key."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "front": "Q",
                "back": "A"
            }
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_update_card_without_api_key(self, async_client):
        """Test that update card requires API key."""
        response = await async_client.put(
            "/flashcards/cards/update",
            params={"card_id": 1, "front": "Updated"}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_delete_card_without_api_key(self, async_client):
        """Test that delete card requires API key."""
        response = await async_client.delete(
            "/flashcards/cards/delete",
            params={"card_id": 1}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_review_card_without_api_key(self, async_client):
        """Test that review card requires API key."""
        response = await async_client.post(
            "/flashcards/cards/review",
            params={"card_id": 1, "ease": 3, "review_time_ms": 5000}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_search_cards_without_api_key(self, async_client):
        """Test that search cards requires API key."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test"}
        )
        assert response.status_code in [401, 403, 422]


class TestCardEndpointsExist:
    """Tests that card endpoints are properly mounted."""

    @pytest.mark.anyio
    async def test_cards_list_endpoint_exists(self, async_client):
        """Test that cards list endpoint exists."""
        response = await async_client.get("/flashcards/cards/list")
        # Should not be 404 (endpoint exists, just needs auth)
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_get_endpoint_exists(self, async_client):
        """Test that cards get endpoint exists."""
        response = await async_client.get(
            "/flashcards/cards/get",
            params={"card_id": 1}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_create_endpoint_exists(self, async_client):
        """Test that cards create endpoint exists."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "front": "Q",
                "back": "A"
            }
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_update_endpoint_exists(self, async_client):
        """Test that cards update endpoint exists."""
        response = await async_client.put(
            "/flashcards/cards/update",
            params={"card_id": 1, "front": "Updated"}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_delete_endpoint_exists(self, async_client):
        """Test that cards delete endpoint exists."""
        response = await async_client.delete(
            "/flashcards/cards/delete",
            params={"card_id": 1}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_review_endpoint_exists(self, async_client):
        """Test that cards review endpoint exists."""
        response = await async_client.post(
            "/flashcards/cards/review",
            params={"card_id": 1, "ease": 3, "review_time_ms": 5000}
        )
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_search_endpoint_exists(self, async_client):
        """Test that cards search endpoint exists."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test"}
        )
        assert response.status_code != 404
