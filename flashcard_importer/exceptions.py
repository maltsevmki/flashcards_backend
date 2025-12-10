"""
Custom exceptions for the flashcard importer module.
These provide clear error messages for different failure scenarios.
"""


class FlashcardImportError(Exception):
    """Base exception for all import-related errors."""
    pass


class FileFormatError(FlashcardImportError):
    """Raised when the file format is not supported or invalid."""

    def __init__(self, filename: str, expected_format: str = None):
        self.filename = filename
        self.expected_format = expected_format
        message = f"Invalid or unsupported file format: '{filename}'"
        if expected_format:
            message += f". Expected: {expected_format}"
        super().__init__(message)


class ParsingError(FlashcardImportError):
    """Raised when there's an error parsing file content."""

    def __init__(self, message: str, line_number: int = None):
        self.line_number = line_number
        if line_number:
            message = f"Line {line_number}: {message}"
        super().__init__(message)


class ValidationError(FlashcardImportError):
    """Raised when card data fails validation."""

    def __init__(self, message: str, card_data: dict = None):
        self.card_data = card_data
        super().__init__(message)


class EmptyFileError(FlashcardImportError):
    """Raised when the file contains no valid cards."""

    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"No valid cards found in file: '{filename}'")


class AnkiDatabaseError(FlashcardImportError):
    """Raised when there's an error reading Anki SQLite database."""

    def __init__(self, message: str, db_path: str = None):
        self.db_path = db_path
        if db_path:
            message = f"{message} (Database: {db_path})"
        super().__init__(message)