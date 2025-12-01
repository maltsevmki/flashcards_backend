from fastapi import APIRouter, Depends
from app.core.security import get_api_key
from app.db import async_session
from app.api.routers.ai.service import Service
from typing import Dict, Any
from app.api.routers.api_methods_enum import APIMethodsEnum


router = APIRouter()

# AI Generation Endpoints
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


@router.post(
    f'/generate-flashcard/{APIMethodsEnum.create.value}',
    dependencies=[Depends(get_api_key)]
)
async def generate_flashcard_from_text(
    text: str,
    deck_name: str,
    type_name: str = "Basic",
    user_timezone_offset_minutes: int = 0
) -> Dict[str, Any]:
    """
    Generate a single flashcard from provided text using AI.
    
    Args:
        text: The source text to generate flashcard from
        deck_name: Name of the deck to add the card to
        type_name: Card type (default: "Basic")
        user_timezone_offset_minutes: User's timezone offset
        
    Returns:
        Dictionary with card_id, front, back, and message
    """
    async with async_session() as session:
        return await Service.generate_flashcard_from_text(
            session=session,
            text=text,
            deck_name=deck_name,
            type_name=type_name,
            user_timezone_offset_minutes=user_timezone_offset_minutes
        )


@router.post(
    f'/generate-multiple/{APIMethodsEnum.create.value}',
    dependencies=[Depends(get_api_key)]
)
async def generate_multiple_flashcards(
    text: str,
    deck_name: str,
    count: int = 5,
    type_name: str = "Basic",
    user_timezone_offset_minutes: int = 0
) -> Dict[str, Any]:
    """
    Generate multiple flashcards from provided text using AI.
    
    Args:
        text: The source text to generate flashcards from
        deck_name: Name of the deck to add the cards to
        count: Number of flashcards to generate (max 10)
        type_name: Card type (default: "Basic")
        user_timezone_offset_minutes: User's timezone offset
        
    Returns:
        Dictionary with list of cards, count, and message
    """
    async with async_session() as session:
        return await Service.generate_multiple_flashcards(
            session=session,
            text=text,
            deck_name=deck_name,
            count=count,
            type_name=type_name,
            user_timezone_offset_minutes=user_timezone_offset_minutes
        )


@router.post(
    f'/improve-flashcard/{APIMethodsEnum.update.value}',
    dependencies=[Depends(get_api_key)]
)
async def improve_flashcard(
    card_id: int,
    improvement_instruction: str = None
) -> Dict[str, Any]:
    """
    Use AI to improve an existing flashcard.
    
    Args:
        card_id: ID of the card to improve
        improvement_instruction: Optional specific instruction for improvement
        
    Returns:
        Dictionary with original and improved versions of the card
    """
    async with async_session() as session:
        return await Service.improve_flashcard(
            session=session,
            card_id=card_id,
            improvement_instruction=improvement_instruction
        )


@router.post(
    f'/suggest-tags/{APIMethodsEnum.get.value}',
    dependencies=[Depends(get_api_key)]
)
async def suggest_tags(
    card_id: int
) -> Dict[str, Any]:
    """
    Use AI to suggest relevant tags for a flashcard.
    
    Args:
        card_id: ID of the card to suggest tags for
        
    Returns:
        Dictionary with current tags and suggested tags
    """
    async with async_session() as session:
        return await Service.suggest_tags(
            session=session,
            card_id=card_id
        )

