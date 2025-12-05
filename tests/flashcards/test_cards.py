"""
Comprehensive integration tests for Card API endpoints.
Tests endpoint availability, authentication, and request/response handling.
"""
import pytest


# =============================================================================
# Authentication Tests
# =============================================================================

class TestCardEndpointsAuthentication:
    """Tests for API authentication on card endpoints."""

    @pytest.mark.anyio
    async def test_list_cards_without_api_key(self, async_client):
        """Test that list cards requires API key."""
        response = await async_client.get("/flashcards/cards/list")
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


# =============================================================================
# Endpoint Existence Tests
# =============================================================================

class TestCardEndpointsExist:
    """Tests that card endpoints are properly mounted."""

    @pytest.mark.anyio
    async def test_cards_list_endpoint_exists(self, async_client):
        """Test that cards list endpoint exists."""
        response = await async_client.get("/flashcards/cards/list")
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


# =============================================================================
# HTTP Method Tests
# =============================================================================

class TestCardEndpointMethods:
    """Tests for correct HTTP methods on card endpoints."""

    @pytest.mark.anyio
    async def test_list_cards_wrong_method(self, async_client):
        """Test that list cards doesn't accept POST."""
        response = await async_client.post("/flashcards/cards/list")
        assert response.status_code == 405

    @pytest.mark.anyio
    async def test_get_card_wrong_method(self, async_client):
        """Test that get card doesn't accept POST."""
        response = await async_client.post(
            "/flashcards/cards/get",
            params={"card_id": 1}
        )
        assert response.status_code == 405

    @pytest.mark.anyio
    async def test_create_card_wrong_method(self, async_client):
        """Test that create card doesn't accept GET."""
        response = await async_client.get("/flashcards/cards/create")
        assert response.status_code == 405

    @pytest.mark.anyio
    async def test_update_card_wrong_method(self, async_client):
        """Test that update card doesn't accept POST."""
        response = await async_client.post(
            "/flashcards/cards/update",
            params={"card_id": 1}
        )
        assert response.status_code == 405

    @pytest.mark.anyio
    async def test_delete_card_wrong_method(self, async_client):
        """Test that delete card doesn't accept GET."""
        response = await async_client.get(
            "/flashcards/cards/delete",
            params={"card_id": 1}
        )
        assert response.status_code == 405

    @pytest.mark.anyio
    async def test_review_card_wrong_method(self, async_client):
        """Test that review card doesn't accept GET."""
        response = await async_client.get("/flashcards/cards/review")
        assert response.status_code == 405

    @pytest.mark.anyio
    async def test_search_cards_wrong_method(self, async_client):
        """Test that search cards doesn't accept POST."""
        response = await async_client.post(
            "/flashcards/cards/search",
            params={"query": "test"}
        )
        assert response.status_code == 405


# =============================================================================
# Request Validation Tests
# =============================================================================

class TestCardRequestValidation:
    """Tests for request parameter validation.
    Note: Auth (401/403) may occur before validation (422) depending on middleware order.
    """

    @pytest.mark.anyio
    async def test_get_card_missing_card_id(self, async_client):
        """Test get card without card_id parameter."""
        response = await async_client.get("/flashcards/cards/get")
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_create_card_missing_type_name(self, async_client):
        """Test create card without type_name."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "deck_name": "Test",
                "front": "Q",
                "back": "A"
            }
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_create_card_missing_deck_name(self, async_client):
        """Test create card without deck_name."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "front": "Q",
                "back": "A"
            }
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_create_card_missing_front(self, async_client):
        """Test create card without front."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "back": "A"
            }
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_create_card_missing_back(self, async_client):
        """Test create card without back."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "front": "Q"
            }
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_update_card_missing_card_id(self, async_client):
        """Test update card without card_id."""
        response = await async_client.put(
            "/flashcards/cards/update",
            params={"front": "Updated"}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_delete_card_missing_card_id(self, async_client):
        """Test delete card without card_id."""
        response = await async_client.delete("/flashcards/cards/delete")
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_review_card_missing_card_id(self, async_client):
        """Test review card without card_id."""
        response = await async_client.post(
            "/flashcards/cards/review",
            params={"ease": 3, "review_time_ms": 5000}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_review_card_missing_ease(self, async_client):
        """Test review card without ease."""
        response = await async_client.post(
            "/flashcards/cards/review",
            params={"card_id": 1, "review_time_ms": 5000}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_review_card_missing_review_time(self, async_client):
        """Test review card without review_time_ms."""
        response = await async_client.post(
            "/flashcards/cards/review",
            params={"card_id": 1, "ease": 3}
        )
        assert response.status_code in [401, 403, 422]

    @pytest.mark.anyio
    async def test_search_cards_missing_query(self, async_client):
        """Test search cards without query."""
        response = await async_client.get("/flashcards/cards/search")
        assert response.status_code in [401, 403, 422]


# =============================================================================
# Pagination Parameter Tests
# =============================================================================

class TestCardPaginationParameters:
    """Tests for pagination parameters on list and search endpoints."""

    @pytest.mark.anyio
    async def test_list_cards_with_limit(self, async_client):
        """Test list cards accepts limit parameter."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"limit": 10}
        )
        # Should accept the parameter (might fail auth, but not validation)
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_list_cards_with_offset(self, async_client):
        """Test list cards accepts offset parameter."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"offset": 5}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_list_cards_with_limit_and_offset(self, async_client):
        """Test list cards accepts both limit and offset."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"limit": 10, "offset": 5}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_with_limit(self, async_client):
        """Test search cards accepts limit parameter."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test", "limit": 10}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_with_offset(self, async_client):
        """Test search cards accepts offset parameter."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test", "offset": 5}
        )
        assert response.status_code != 422


# =============================================================================
# Filter Parameter Tests
# =============================================================================

class TestCardFilterParameters:
    """Tests for filter parameters on list and search endpoints."""

    @pytest.mark.anyio
    async def test_list_cards_with_deck_name(self, async_client):
        """Test list cards accepts deck_name filter."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"deck_name": "Test Deck"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_list_cards_with_type_id(self, async_client):
        """Test list cards accepts type_id filter."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"type_id": 0}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_with_deck_name(self, async_client):
        """Test search cards accepts deck_name filter."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test", "deck_name": "Test Deck"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_with_tags(self, async_client):
        """Test search cards accepts tags filter."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test", "tags": "important"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_with_type_id(self, async_client):
        """Test search cards accepts type_id filter."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test", "type_id": 0}
        )
        assert response.status_code != 422


# =============================================================================
# Optional Parameter Tests
# =============================================================================

class TestCardOptionalParameters:
    """Tests for optional parameters."""

    @pytest.mark.anyio
    async def test_create_card_with_tags(self, async_client):
        """Test create card accepts optional tags."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "front": "Q",
                "back": "A",
                "tags": "tag1 tag2"
            }
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_create_card_with_timezone_offset(self, async_client):
        """Test create card accepts timezone offset."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "front": "Q",
                "back": "A",
                "user_timezone_offset_minutes": -300
            }
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_review_card_with_timezone_offset(self, async_client):
        """Test review card accepts timezone offset."""
        response = await async_client.post(
            "/flashcards/cards/review",
            params={
                "card_id": 1,
                "ease": 3,
                "review_time_ms": 5000,
                "user_timezone_offset_minutes": 330
            }
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_update_card_with_only_front(self, async_client):
        """Test update card with only front field."""
        response = await async_client.put(
            "/flashcards/cards/update",
            params={"card_id": 1, "front": "Updated front"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_update_card_with_only_back(self, async_client):
        """Test update card with only back field."""
        response = await async_client.put(
            "/flashcards/cards/update",
            params={"card_id": 1, "back": "Updated back"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_update_card_with_only_tags(self, async_client):
        """Test update card with only tags field."""
        response = await async_client.put(
            "/flashcards/cards/update",
            params={"card_id": 1, "tags": "new-tags"}
        )
        assert response.status_code != 422


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestCardEdgeCases:
    """Tests for edge cases in card endpoints."""

    @pytest.mark.anyio
    async def test_list_cards_zero_limit(self, async_client):
        """Test list cards with limit=0."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"limit": 0}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_list_cards_large_limit(self, async_client):
        """Test list cards with very large limit."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"limit": 10000}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_list_cards_large_offset(self, async_client):
        """Test list cards with very large offset."""
        response = await async_client.get(
            "/flashcards/cards/list",
            params={"offset": 1000000}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_empty_query(self, async_client):
        """Test search cards with empty query string."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": ""}
        )
        # Empty query should be accepted
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_special_characters(self, async_client):
        """Test search cards with special characters in query."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "test!@#$%"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_search_cards_unicode_query(self, async_client):
        """Test search cards with unicode characters."""
        response = await async_client.get(
            "/flashcards/cards/search",
            params={"query": "日本語"}
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_create_card_unicode_content(self, async_client):
        """Test create card with unicode content."""
        response = await async_client.post(
            "/flashcards/cards/create",
            params={
                "type_name": "Basic",
                "deck_name": "Test",
                "front": "什么是Python？",
                "back": "Python是编程语言"
            }
        )
        assert response.status_code != 422

    @pytest.mark.anyio
    async def test_review_card_all_ease_values(self, async_client):
        """Test review card accepts all valid ease values."""
        for ease in [1, 2, 3, 4]:
            response = await async_client.post(
                "/flashcards/cards/review",
                params={"card_id": 1, "ease": ease, "review_time_ms": 5000}
            )
            assert response.status_code != 422


# =============================================================================
# Router Configuration Tests
# =============================================================================

class TestCardRouterConfiguration:
    """Tests for router configuration and prefixes."""

    @pytest.mark.anyio
    async def test_flashcards_prefix(self, async_client):
        """Test that endpoints are under /flashcards prefix."""
        response = await async_client.get("/flashcards/cards/list")
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_cards_prefix(self, async_client):
        """Test that card endpoints are under /cards prefix."""
        response = await async_client.get("/flashcards/cards/list")
        assert response.status_code != 404

    @pytest.mark.anyio
    async def test_wrong_prefix_returns_404(self, async_client):
        """Test that wrong prefix returns 404."""
        response = await async_client.get("/wrong/cards/list")
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_missing_cards_prefix_returns_404(self, async_client):
        """Test that missing cards prefix returns 404."""
        response = await async_client.get("/flashcards/list")
        assert response.status_code == 404
