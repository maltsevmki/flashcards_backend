import logging
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ImportLogEntry:
    level: LogLevel
    message: str
    line_number: Optional[int] = None
    field_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self):
        parts = [f"[{self.level.value.upper()}]"]
        if self.line_number:
            parts.append(f"Line {self.line_number}:")
        if self.field_name:
            parts.append(f"({self.field_name})")
        parts.append(self.message)
        return " ".join(parts)


class ImportLogger:
    """Logger for tracking import operations with detailed diagnostics."""
    
    def __init__(self, source_file: str = None):
        self.source_file = source_file
        self.entries: List[ImportLogEntry] = []
        self._warnings_count = 0
        self._errors_count = 0
        
        # Configure Python logging
        self._logger = logging.getLogger(f"flashcard_importer.{source_file or 'unknown'}")
    
    def debug(self, message: str, line_number: int = None, field_name: str = None):
        entry = ImportLogEntry(LogLevel.DEBUG, message, line_number, field_name)
        self.entries.append(entry)
        self._logger.debug(str(entry))
    
    def info(self, message: str, line_number: int = None, field_name: str = None):
        entry = ImportLogEntry(LogLevel.INFO, message, line_number, field_name)
        self.entries.append(entry)
        self._logger.info(str(entry))
    
    def warning(self, message: str, line_number: int = None, field_name: str = None):
        entry = ImportLogEntry(LogLevel.WARNING, message, line_number, field_name)
        self.entries.append(entry)
        self._warnings_count += 1
        self._logger.warning(str(entry))
    
    def error(self, message: str, line_number: int = None, field_name: str = None):
        entry = ImportLogEntry(LogLevel.ERROR, message, line_number, field_name)
        self.entries.append(entry)
        self._errors_count += 1
        self._logger.error(str(entry))
    
    @property
    def warnings_count(self) -> int:
        return self._warnings_count
    
    @property
    def errors_count(self) -> int:
        return self._errors_count
    
    def get_warnings(self) -> List[ImportLogEntry]:
        return [e for e in self.entries if e.level == LogLevel.WARNING]
    
    def get_errors(self) -> List[ImportLogEntry]:
        return [e for e in self.entries if e.level == LogLevel.ERROR]
    
    def get_summary(self) -> str:
        return (
            f"Import Log Summary:\n"
            f"  Source: {self.source_file}\n"
            f"  Total entries: {len(self.entries)}\n"
            f"  Warnings: {self._warnings_count}\n"
            f"  Errors: {self._errors_count}"
        )

