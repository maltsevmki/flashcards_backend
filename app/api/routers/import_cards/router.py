"""FastAPI router for flashcard import endpoints."""
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.api.routers.import_cards.service import ImportService
from flashcard_importer.exceptions import FlashcardImportError, FileFormatError


router = APIRouter(prefix="/import", tags=["Import"])


# Response Models
class ImportSummary(BaseModel):
    total_imported: int
    total_skipped: int
    success_rate: float
    deck_detected: bool


class ImportStatistics(BaseModel):
    deck_distribution: dict
    top_tags: dict
    cards_with_html: int
    cards_with_cloze: int


class ImportResponse(BaseModel):
    success: bool
    summary: ImportSummary
    cards: List[dict]
    statistics: ImportStatistics
    available_decks: Optional[List[str]]
    warnings: List[str]
    errors: List[str]


class PreviewResponse(BaseModel):
    filename: str
    format: str
    settings: dict
    available_decks: Optional[List[str]]
    total_cards: int
    sample_cards: List[dict]
    has_deck_info: bool


class SupportedFormatsResponse(BaseModel):
    formats: List[str]
    description: dict


@router.get("/formats", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    """Get list of supported import formats."""
    formats = ImportService.get_supported_formats()
    
    descriptions = {
        '.txt': 'Anki text export (tab-separated with optional headers)',
        '.csv': 'Comma-separated values',
        '.tsv': 'Tab-separated values',
        '.xlsx': 'Microsoft Excel workbook',
        '.xls': 'Microsoft Excel 97-2003 workbook',
        '.apkg': 'Anki deck package',
        '.colpkg': 'Anki collection package'
    }
    
    return {
        'formats': formats,
        'description': {fmt: descriptions.get(fmt, 'Unknown') for fmt in formats}
    }


@router.post("/preview", response_model=PreviewResponse)
async def preview_import(
    file: UploadFile = File(..., description="File to preview")
):
    """
    Preview the contents of a file before importing.
    Shows format detection, available decks, and sample cards.
    """
    try:
        result = await ImportService.preview_file(file, limit=5)
        return result
    except FileFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FlashcardImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.post("/upload", response_model=ImportResponse)
async def import_flashcards(
    file: UploadFile = File(..., description="File to import"),
    default_deck: Optional[str] = Form(None, description="Default deck for cards without deck info"),
    auto_assign_decks: bool = Form(False, description="Use AI to suggest deck assignments"),
    strip_html: bool = Form(False, description="Remove HTML tags from card content"),
    deck_filter: Optional[str] = Form(None, description="Only import cards from this deck (APKG only)")
):
    """
    Import flashcards from a file.
    
    Supported formats: .txt, .csv, .tsv, .xlsx, .xls, .apkg, .colpkg
    
    Options:
    - **default_deck**: Assign this deck to cards without deck information
    - **auto_assign_decks**: Use AI to analyze content and suggest deck names
    - **strip_html**: Remove HTML tags from card content
    - **deck_filter**: For Anki packages, only import cards from the specified deck
    """
    try:
        result = await ImportService.import_from_file(
            file=file,
            default_deck=default_deck,
            auto_assign_decks=auto_assign_decks,
            strip_html=strip_html,
            deck_filter=deck_filter
        )
        return result
    except FileFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FlashcardImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/validate")
async def validate_file(
    file: UploadFile = File(..., description="File to validate")
):
    """
    Validate a file without importing.
    Returns validation status and any issues found.
    """
    try:
        preview = await ImportService.preview_file(file, limit=0)
        
        issues = []
        
        if preview['total_cards'] == 0:
            issues.append("No valid cards found in file")
        
        if not preview['has_deck_info']:
            issues.append("No deck information found - cards will need deck assignment")
        
        return {
            'valid': len(issues) == 0 or preview['total_cards'] > 0,
            'filename': preview['filename'],
            'format': preview['format'],
            'total_cards': preview['total_cards'],
            'issues': issues,
            'can_import': preview['total_cards'] > 0
        }
    except FileFormatError as e:
        return {
            'valid': False,
            'filename': file.filename,
            'format': None,
            'total_cards': 0,
            'issues': [str(e)],
            'can_import': False
        }
    except Exception as e:
        return {
            'valid': False,
            'filename': file.filename,
            'format': None,
            'total_cards': 0,
            'issues': [f"Validation error: {str(e)}"],
            'can_import': False
        }

