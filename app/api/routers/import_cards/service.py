"""Service layer for flashcard import operations."""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import UploadFile

from flashcard_importer import ParserFactory, Flashcard, ImportResult
from flashcard_importer.utils import (
    DeckDetector,
    MissingDeckHandler,
    HtmlHandler,
    ImportLogger
)
from flashcard_importer.exceptions import FlashcardImportError, FileFormatError


class ImportService:
    """Service for importing flashcards from various file formats."""
    
    ALLOWED_EXTENSIONS = {'.txt', '.csv', '.tsv', '.xlsx', '.xls', '.apkg', '.colpkg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported file formats."""
        return list(cls.ALLOWED_EXTENSIONS)
    
    @classmethod
    async def import_from_file(
        cls,
        file: UploadFile,
        default_deck: Optional[str] = None,
        auto_assign_decks: bool = False,
        strip_html: bool = False,
        deck_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import flashcards from an uploaded file.
        
        Args:
            file: The uploaded file
            default_deck: Default deck name for cards without deck
            auto_assign_decks: Use AI to suggest deck assignments
            strip_html: Strip HTML from card content
            deck_filter: Only import cards from this deck (APKG only)
            
        Returns:
            Dictionary with import results and statistics
        """
        logger = ImportLogger(source_file=file.filename)
        
        # Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise FileFormatError(
                file.filename, 
                f"Supported formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp(prefix='flashcard_import_')
        temp_file = os.path.join(temp_dir, file.filename)
        
        try:
            # Write uploaded content to temp file
            with open(temp_file, 'wb') as f:
                content = await file.read()
                
                # Check file size
                if len(content) > cls.MAX_FILE_SIZE:
                    raise FlashcardImportError(
                        f"File too large. Maximum size is {cls.MAX_FILE_SIZE // (1024*1024)}MB"
                    )
                
                f.write(content)
            
            logger.info(f"Processing file: {file.filename}")
            
            # Create parser and parse file
            parser = ParserFactory.create(temp_file)
            
            # For APKG files, support deck filtering
            if ext in ['.apkg', '.colpkg'] and deck_filter:
                result = parser.parse(deck_filter=deck_filter)
            else:
                result = parser.parse()
            
            logger.info(f"Parsed {len(result.cards)} cards")
            
            # Process cards
            processed_cards = cls._process_cards(
                cards=result.cards,
                default_deck=default_deck,
                auto_assign_decks=auto_assign_decks,
                strip_html=strip_html,
                logger=logger
            )
            
            # Build response
            return cls._build_response(
                result=result,
                processed_cards=processed_cards,
                logger=logger,
                parser=parser,
                ext=ext
            )
            
        finally:
            # Cleanup temp files
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @classmethod
    def _process_cards(
        cls,
        cards: List[Flashcard],
        default_deck: Optional[str],
        auto_assign_decks: bool,
        strip_html: bool,
        logger: ImportLogger
    ) -> List[Dict]:
        """Process imported cards with options."""
        
        # Handle missing deck info
        coverage = DeckDetector.analyze_deck_coverage(cards)
        
        if coverage['cards_without_deck'] > 0:
            if auto_assign_decks:
                counts = MissingDeckHandler.assign_suggested_decks(cards)
                logger.info(f"Auto-assigned decks: {counts}")
            elif default_deck:
                modified = MissingDeckHandler.assign_default_deck(cards, default_deck)
                logger.info(f"Assigned default deck '{default_deck}' to {modified} cards")
            else:
                warning = MissingDeckHandler.get_warning_message(
                    coverage['cards_without_deck'],
                    coverage['total_cards']
                )
                logger.warning(warning)
        
        # Process each card
        processed = []
        for card in cards:
            card_data = card.to_dict()
            
            # Strip HTML if requested
            if strip_html:
                card_data['front'] = HtmlHandler.strip_html(card_data['front'])
                card_data['back'] = HtmlHandler.strip_html(card_data['back'])
                card_data['html_enabled'] = False
            
            # Add preview text
            card_data['front_preview'] = HtmlHandler.sanitize_for_display(
                card_data['front'], max_length=100
            )
            card_data['back_preview'] = HtmlHandler.sanitize_for_display(
                card_data['back'], max_length=100
            )
            
            processed.append(card_data)
        
        return processed
    
    @classmethod
    def _build_response(
        cls,
        result: ImportResult,
        processed_cards: List[Dict],
        logger: ImportLogger,
        parser: Any,
        ext: str
    ) -> Dict[str, Any]:
        """Build the response dictionary."""
        
        # Get deck info for APKG files
        available_decks = None
        if ext in ['.apkg', '.colpkg']:
            available_decks = list(parser.get_decks().values())
        
        # Analyze cards
        deck_distribution = {}
        tag_counts = {}
        
        for card in processed_cards:
            # Count by deck
            deck = card.get('deck_name') or 'No Deck'
            deck_distribution[deck] = deck_distribution.get(deck, 0) + 1
            
            # Count tags
            for tag in card.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'success': True,
            'summary': {
                'total_imported': len(processed_cards),
                'total_skipped': result.skipped_count,
                'success_rate': result.success_rate,
                'deck_detected': result.deck_detected
            },
            'cards': processed_cards,
            'statistics': {
                'deck_distribution': deck_distribution,
                'top_tags': dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:10]),
                'cards_with_html': sum(1 for c in processed_cards if c.get('html_enabled')),
                'cards_with_cloze': sum(1 for c in processed_cards if c.get('card_type') == 'cloze')
            },
            'available_decks': available_decks,
            'warnings': [str(w) for w in logger.get_warnings()],
            'errors': [str(e) for e in result.errors]
        }
    
    @classmethod
    async def preview_file(cls, file: UploadFile, limit: int = 5) -> Dict[str, Any]:
        """
        Preview the contents of an import file without full processing.
        
        Args:
            file: The uploaded file
            limit: Maximum number of cards to preview
            
        Returns:
            Preview information about the file
        """
        ext = Path(file.filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise FileFormatError(
                file.filename, 
                f"Supported formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
        
        temp_dir = tempfile.mkdtemp(prefix='flashcard_preview_')
        temp_file = os.path.join(temp_dir, file.filename)
        
        try:
            with open(temp_file, 'wb') as f:
                content = await file.read()
                f.write(content)
            
            parser = ParserFactory.create(temp_file)
            settings = parser.detect_settings()
            
            # For APKG, get deck list
            decks = None
            if ext in ['.apkg', '.colpkg']:
                decks = list(parser.get_decks().values())
            
            # Parse a sample
            result = parser.parse()
            sample_cards = [c.to_dict() for c in result.cards[:limit]]
            
            return {
                'filename': file.filename,
                'format': ext,
                'settings': settings,
                'available_decks': decks,
                'total_cards': len(result.cards),
                'sample_cards': sample_cards,
                'has_deck_info': result.deck_detected
            }
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

