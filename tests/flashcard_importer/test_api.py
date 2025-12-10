"""Tests for the import API endpoints."""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO

# Note: These tests require the FastAPI app to be running
# Run with: pytest tests/flashcard_importer/test_api.py -v


@pytest.fixture
def sample_txt_file():
    """Create a sample TXT file for testing."""
    content = b"Question 1\tAnswer 1\nQuestion 2\tAnswer 2"
    return BytesIO(content)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    content = b"front,back,deck,tags\nQ1,A1,TestDeck,tag1\nQ2,A2,TestDeck,tag2"
    return BytesIO(content)


@pytest.fixture
def anki_txt_file():
    """Create an Anki-style TXT file for testing."""
    content = b"""#separator:tab
#html:true
#deck column:3
What is Python?\tA programming language\tProgramming
What is Java?\tAnother programming language\tProgramming
"""
    return BytesIO(content)


class TestImportFormats:
    """Test the /import/formats endpoint."""
    
    def test_get_formats(self, client):
        response = client.get("/import/formats")
        assert response.status_code == 200
        
        data = response.json()
        assert 'formats' in data
        assert '.txt' in data['formats']
        assert '.csv' in data['formats']
        assert '.apkg' in data['formats']


class TestImportPreview:
    """Test the /import/preview endpoint."""
    
    def test_preview_txt(self, client, sample_txt_file):
        response = client.post(
            "/import/preview",
            files={"file": ("test.txt", sample_txt_file, "text/plain")}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data['filename'] == "test.txt"
        assert data['format'] == ".txt"
        assert data['total_cards'] >= 0
    
    def test_preview_invalid_format(self, client):
        content = BytesIO(b"test content")
        response = client.post(
            "/import/preview",
            files={"file": ("test.xyz", content, "application/octet-stream")}
        )
        assert response.status_code == 400


class TestImportUpload:
    """Test the /import/upload endpoint."""
    
    def test_upload_txt(self, client, sample_txt_file):
        response = client.post(
            "/import/upload",
            files={"file": ("test.txt", sample_txt_file, "text/plain")}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
        assert 'cards' in data
        assert 'summary' in data
    
    def test_upload_csv_with_options(self, client, sample_csv_file):
        response = client.post(
            "/import/upload",
            files={"file": ("test.csv", sample_csv_file, "text/csv")},
            data={
                "default_deck": "MyDefaultDeck",
                "strip_html": "false"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] == True
    
    def test_upload_with_auto_assign_decks(self, client, sample_txt_file):
        response = client.post(
            "/import/upload",
            files={"file": ("test.txt", sample_txt_file, "text/plain")},
            data={"auto_assign_decks": "true"}
        )
        assert response.status_code == 200
    
    def test_upload_invalid_format(self, client):
        content = BytesIO(b"test content")
        response = client.post(
            "/import/upload",
            files={"file": ("test.pdf", content, "application/pdf")}
        )
        assert response.status_code == 400


class TestImportValidate:
    """Test the /import/validate endpoint."""
    
    def test_validate_valid_file(self, client, sample_txt_file):
        response = client.post(
            "/import/validate",
            files={"file": ("test.txt", sample_txt_file, "text/plain")}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'valid' in data
        assert 'can_import' in data
    
    def test_validate_invalid_format(self, client):
        content = BytesIO(b"test content")
        response = client.post(
            "/import/validate",
            files={"file": ("test.xyz", content, "application/octet-stream")}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data['valid'] == False
        assert data['can_import'] == False


# Fixture for test client - adjust based on your app structure
@pytest.fixture
def client():
    """Create test client. Adjust import based on your app structure."""
    try:
        from app.main import app
        return TestClient(app)
    except ImportError:
        pytest.skip("FastAPI app not available")

