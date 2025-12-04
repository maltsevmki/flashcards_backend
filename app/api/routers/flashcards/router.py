from fastapi import APIRouter, Depends
from app.core.security import get_api_key
from app.db import async_session
from app.api.routers.flashcards.service import Service
from app.api.routers.api_methods_enum import APIMethodsEnum
from app.api.routers.flashcards.prefix_enum import PrefixEnum
from app.schemas.flashcards.input.card import (
    FlashcardCreateInput,
    FlashcardReviewInput,
    FlashcardListInput,
    FlashcardUpdateInput,
    FlashcardDeleteInput,
    FlashcardGetInput
)
from app.schemas.flashcards.input.deck import (
    DeckDeleteInput,
    DeckGetInput,
    DeckUpdateInput,
    DeckCreateInput,
    DeckListInput
)
from app.schemas.flashcards.output.deck import (
    DeckGetOutput,
    DeckDeleteOutput,
    DeckUpdateOutput,
    DeckListOutput,
    DeckCreateOutput
)
from app.schemas.flashcards.output.card import (
    FlashcardCreateOutput,
    FlashcardGetOutput,
    FlashcardUpdateOutput,
    FlashcardReviewOutput,
    FlashcardDeleteOutput,
    FlashcardListOutput
)


router = APIRouter()

# Cards
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


@router.get(
    f'/{PrefixEnum.cards.value}/{APIMethodsEnum.list.value}',
    response_model=FlashcardListOutput,
    dependencies=[Depends(get_api_key)]
)
async def list_cards(
    deck_name: str = None,
    type_id: int = None,
    limit: int = 100,
    offset: int = 0
) -> FlashcardListOutput:
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
    f'/{PrefixEnum.cards.value}/{APIMethodsEnum.get.value}',
    response_model=FlashcardGetOutput,
    dependencies=[Depends(get_api_key)]
)
async def get_flashcard(card_id: int) -> FlashcardGetOutput:
    async with async_session() as session:
        return await Service.get_card(
            session=session,
            data=FlashcardGetInput(card_id=card_id)
        )


@router.post(
    f'/{PrefixEnum.cards.value}/{APIMethodsEnum.review.value}',
    response_model=FlashcardReviewOutput,
    dependencies=[Depends(get_api_key)])
async def review_card(
    card_id: int,
    ease: int,
    review_time_ms: int,
    user_timezone_offset_minutes: int = 0
) -> FlashcardReviewOutput:
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
    f'/{PrefixEnum.cards.value}/{APIMethodsEnum.create.value}',
    response_model=FlashcardCreateOutput,
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
    f'/{PrefixEnum.cards.value}/{APIMethodsEnum.update.value}',
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
    f'/{PrefixEnum.cards.value}/{APIMethodsEnum.delete.value}',
    response_model=FlashcardDeleteOutput,
    dependencies=[Depends(get_api_key)]
)
async def delete_flashcard(
    card_id: int,
    user_timezone_offset_minutes: int = 0
) -> FlashcardDeleteOutput:
    async with async_session() as session:
        return await Service.delete_card(
            session=session,
            data=FlashcardDeleteInput(
                card_id=card_id,
                user_timezone_offset_minutes=user_timezone_offset_minutes
            )
        )


# Decks
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


@router.post(
    f'/{PrefixEnum.decks.value}/{APIMethodsEnum.create.value}',
    response_model=DeckCreateOutput,
    dependencies=[Depends(get_api_key)]
)
async def create_deck(
    name: str,
) -> DeckCreateOutput:
    async with async_session() as session:
        return await Service.create_deck(
            session=session,
            data=DeckCreateInput(
                name=name
            )
        )


@router.get(
    f'/{PrefixEnum.decks.value}/{APIMethodsEnum.list.value}',
    response_model=DeckListOutput,
    dependencies=[Depends(get_api_key)],
)
async def list_decks(
    limit: int = 100,
    offset: int = 0
) -> DeckListOutput:
    async with async_session() as session:
        return await Service.list_decks(
            session=session,
            data=DeckListInput(
                limit=limit,
                offset=offset
            )
        )


@router.get(
    f'/{PrefixEnum.decks.value}/{APIMethodsEnum.get.value}',
    response_model=DeckGetOutput,
    dependencies=[Depends(get_api_key)]
)
async def get_deck(deck_id: int) -> DeckGetOutput:
    async with async_session() as session:
        return await Service.get_deck(
            session=session,
            data=DeckGetInput(
                deck_id=deck_id
            )
        )


@router.delete(
    f'/{PrefixEnum.decks.value}/{APIMethodsEnum.delete.value}',
    response_model=DeckDeleteOutput,
    dependencies=[Depends(get_api_key)]
)
async def delete_deck(
    deck_id: int,
    user_timezone_offset_minutes: int = 0
) -> DeckDeleteOutput:
    async with async_session() as session:
        return await Service.delete_deck(
            session=session,
            data=DeckDeleteInput(
                deck_id=deck_id,
                user_timezone_offset_minutes=user_timezone_offset_minutes
            )
        )


@router.put(
    f'/{PrefixEnum.decks.value}/{APIMethodsEnum.update.value}',
    response_model=DeckUpdateOutput,
    dependencies=[Depends(get_api_key)]
)
async def update_deck(
    deck_id: int,
    name: str = None,
    config_id: int = None,
    user_timezone_offset_minutes: int = 0
) -> DeckUpdateOutput:
    async with async_session() as session:
        return await Service.update_deck(
            session=session,
            data=DeckUpdateInput(
                deck_id=deck_id,
                new_name=name,
                config_id=config_id,
                user_timezone_offset_minutes=user_timezone_offset_minutes
            )
        )
