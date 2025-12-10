"""
Abstract base class for all file parsers.
Defines the interface that all parsers must implement.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List

from flashcard_importer.models.flashcard import Flashcard, ImportResult
from flashcard_importer.exceptions import FileFormatError


class BaseParser(ABC):

    # Subclasses should override this with their supported extensions
    SUPPORTED_EXTENSIONS: List[str] = []

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self._validate_file()

    def _validate_file(self) -> None:
        # Check file exists
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Check extension is supported
        extension = self.file_path.suffix.lower()
        if self.SUPPORTED_EXTENSIONS and extension not in self.SUPPORTED_EXTENSIONS:
            raise FileFormatError(
                str(self.file_path),
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

    @abstractmethod
    def parse(self) -> ImportResult:

        pass

    @abstractmethod
    def detect_settings(self) -> dict:
        """
        Detect file-specific settings (separator, HTML mode, etc.)

        Returns:
            Dictionary of detected settings
        """
        pass

    def get_file_info(self) -> dict:
        return {
            "filename": self.file_path.name,
            "extension": self.file_path.suffix.lower(),
            "size_bytes": self.file_path.stat().st_size,
            "path": str(self.file_path.absolute())
        }


class ParserFactory:
    """
    Factory class to create the appropriate parser based on file extension.

    Usage:
        # Register parsers (done once when parsers are created)
        ParserFactory.register('.txt', TxtParser)
        ParserFactory.register('.csv', CsvParser)

        # Create parser for a file
        parser = ParserFactory.create('my_cards.txt')
        result = parser.parse()
    """

    _parsers = {}  # Extension -> Parser class mapping

    @classmethod
    def register(cls, extension: str, parser_class: type) -> None:
        """
        Register a parser class for a file extension.

        Args:
            extension: File extension (e.g., '.txt')
            parser_class: Parser class to use for this extension
        """
        cls._parsers[extension.lower()] = parser_class

    @classmethod
    def create(cls, file_path: Union[str, Path]) -> BaseParser:
        """
        Create the appropriate parser for the given file.

        Args:
            file_path: Path to the file to parse

        Returns:
            Parser instance appropriate for the file type

        Raises:
            FileFormatError: If no parser is registered for this extension
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension not in cls._parsers:
            supported = ', '.join(cls._parsers.keys()) if cls._parsers else 'None registered'
            raise FileFormatError(
                str(path),
                f"Supported formats: {supported}"
            )

        return cls._parsers[extension](file_path)

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        return list(cls._parsers.keys())

    @classmethod
    def is_supported(cls, file_path: Union[str, Path]) -> bool:
        extension = Path(file_path).suffix.lower()
        return extension in cls._parsers

    @classmethod
    def clear(cls) -> None:
        """Clear all registered parsers (useful for testing)."""
        cls._parsers = {}