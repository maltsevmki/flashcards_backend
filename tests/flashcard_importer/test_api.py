"""Integration tests for the import API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from io import BytesIO

from app.main import app


@pytest.fixture
def test_csv_content():
    """Create test CSV content."""
    content = "front,back,deck,tags\n"
    content += "Question1,Answer1,TestDeck,tag1\n"
    content += "Question2,Answer2,TestDeck,tag2\n"
    return content.encode()


@pytest.fixture
def test_txt_content():
    """Create test TXT content."""
    return b"Question1\tAnswer1\nQuestion2\tAnswer2\n"


@pytest.fixture
def invalid_file_content():
    """Create invalid file content."""
    return b"invalid content without proper format"


class TestImportEndpoints:
    """Test class for import API endpoints."""

    @pytest.mark.asyncio
    async def test_get_supported_formats(self):
        """Test getting list of supported formats."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/import/formats")
            assert response.status_code == 200
            data = response.json()
            assert "formats" in data
            assert ".txt" in data["formats"]
            assert ".csv" in data["formats"]
            assert ".xlsx" in data["formats"]
            assert ".apkg" in data["formats"]

    @pytest.mark.asyncio
    async def test_preview_csv_file(self, test_csv_content):
        """Test previewing a CSV file."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
            response = await client.post("/import/preview", files=files)
            assert response.status_code == 200
            data = response.json()
            assert "sample_cards" in data
            assert "total_cards" in data
            assert "settings" in data

    @pytest.mark.asyncio
    async def test_upload_csv_file(self, test_csv_content):
        """Test uploading and importing a CSV file."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
            response = await client.post("/import/upload", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert "summary" in data
            assert data["summary"]["total_imported"] == 2

    @pytest.mark.asyncio
    async def test_upload_txt_file(self, test_txt_content):
        """Test uploading and importing a TXT file."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.txt", BytesIO(test_txt_content), "text/plain")}
            response = await client.post("/import/upload", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data["summary"]["total_imported"] == 2

    @pytest.mark.asyncio
    async def test_upload_with_default_deck(self, test_csv_content):
        """Test uploading with default deck specified."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
            data_form = {"default_deck": "CustomDeck"}
            response = await client.post(
                "/import/upload", files=files, data=data_form
            )
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True

    @pytest.mark.asyncio
    async def test_upload_unsupported_format(self):
        """Test uploading an unsupported file format."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {
                "file": ("test.xyz", BytesIO(b"content"), "application/octet-stream")
            }
            response = await client.post("/import/upload", files=files)
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data

    @pytest.mark.asyncio
    async def test_validate_valid_file(self, test_csv_content):
        """Test validating a valid file."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {"file": ("test.csv", BytesIO(test_csv_content), "text/csv")}
            response = await client.post("/import/validate", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data['valid'] is True
            assert data['can_import'] is True

    @pytest.mark.asyncio
    async def test_validate_invalid_format(self):
        """Test validating an unsupported format."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            files = {
                "file": ("test.xyz", BytesIO(b"content"), "application/octet-stream")
            }
            response = await client.post("/import/validate", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data['valid'] is False
            assert data['can_import'] is False
