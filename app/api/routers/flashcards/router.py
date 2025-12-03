from fastapi import APIRouter, Depends
from app.core.security import get_api_key
from app.db import async_session
from app.api.routers.flashcards.service import Service
from typing import List
from app.api.routers.api_methods_enum import APIMethodsEnum

from app.schemas.flashcards.input.card import (
    FlashcardCreateInput,
    FlashcardReviewInput,
    FlashcardListInput,
    FlashcardUpdateInput,
    FlashcardDeleteInput,
)
from app.schemas.flashcards.output.card import (
    FlashcardCreateOutput,
    FlashcardListItemOutput,
    FlashcardGetOutput,
    FlashcardUpdateOutput,
    FlashcardDeleteOutput
)


router = APIRouter()

# Cards
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


@router.get(
    f'/cards/{APIMethodsEnum.list.value}',
    response_model=List[FlashcardListItemOutput]
)
async def list_cards(
    deck_name: str = None,
    type_id: int = None,
    limit: int = 100,
    offset: int = 0
):
    async with async_session() as session:
        return await Service.list_cards(
            session=session,
            data=FlashcardListInput(
                deck_name=deck_name,
                type_id=type_id,
                limit=limit,
                offset=offset
            )
        )


@router.get(
    f'/cards/{APIMethodsEnum.get.value}',
    response_model=FlashcardGetOutput,
    dependencies=[Depends(get_api_key)]
)
async def get_flashcard(card_id: int):
    async with async_session() as session:
        return await Service.get_card(
            session=session,
            card_id=card_id
        )


@router.post(
    f'/cards/{APIMethodsEnum.review.value}',
    dependencies=[Depends(get_api_key)])
async def review_card(
    card_id: int,
    ease: int,
    review_time_ms: int,
    user_timezone_offset_minutes: int = 0
):
    async with async_session() as session:
        return await Service.review_card(
            session=session,
            data=FlashcardReviewInput(
                card_id=card_id,
                ease=ease,
                review_time_ms=review_time_ms,
                user_timezone_offset_minutes=user_timezone_offset_minutes
            )
        )


@router.post(
    f'/cards/{APIMethodsEnum.create.value}',
    dependencies=[Depends(get_api_key)])
async def create_flashcard(
    type_name: str,
    deck_name: str,
    front: str,
    back: str,
    tags: str = '',
    user_timezone_offset_minutes: int = 0
) -> FlashcardCreateOutput:
    async with async_session() as session:
        return await Service.create_card(
            session=session,
            data=FlashcardCreateInput(
                type_name=type_name,
                deck_name=deck_name,
                front=front,
                back=back,
                tags=tags,
                user_timezone_offset_minutes=user_timezone_offset_minutes
            )
        )


@router.put(
    f'/cards/{APIMethodsEnum.update.value}',
    response_model=FlashcardUpdateOutput,
    dependencies=[Depends(get_api_key)]
)
async def update_flashcard(
    card_id: int,
    front: str = None,
    back: str = None,
    tags: str = None,
    user_timezone_offset_minutes: int = 0
) -> FlashcardUpdateOutput:
    async with async_session() as session:
        return await Service.update_card(
            session=session,
            data=FlashcardUpdateInput(
                card_id=card_id,
                front=front,
                back=back,
                tags=tags,
                user_timezone_offset_minutes=user_timezone_offset_minutes
            )
        )


@router.delete(
    f'/cards/{APIMethodsEnum.delete.value}',
    response_model=FlashcardDeleteOutput,
    dependencies=[Depends(get_api_key)]
)
async def delete_flashcard(
    card_id: int,
) -> FlashcardDeleteOutput:
    async with async_session() as session:
        return await Service.delete_card(
            session=session,
            data=FlashcardDeleteInput(
                card_id=card_id
            )
        )

# Decks
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
