from fastapi import APIRouter, Depends
from app.core.security import get_api_key
from app.db import async_session
from app.api.routers.flashcards.service import CardService
from app.schemas.flashcards.input.card import FlashcardCreateInput
from app.schemas.flashcards.output.card import FlashcardCreateOutput


router = APIRouter()


@router.get('/', dependencies=[Depends(get_api_key)])
async def list_flashcards():
    return {'message': 'TO DO'}


@router.get('/', dependencies=[Depends(get_api_key)])
async def get_flashcard():
    return {'message': 'TO DO'}


@router.post('/', dependencies=[Depends(get_api_key)])
async def create_flashcard(data: FlashcardCreateInput) -> FlashcardCreateOutput:
    async with async_session() as session:
        return await CardService.create_card(
            session=session,
            data=data
        )


@router.put('/', dependencies=[Depends(get_api_key)])
async def update_flashcard():
    return {'message': 'TO DO'}


@router.delete('/', dependencies=[Depends(get_api_key)])
async def delete_flashcard():
    return {'message': 'TO DO'}
