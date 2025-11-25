from fastapi import APIRouter, Depends
from app.core.security import get_api_key


router = APIRouter()


@router.get('/', dependencies=[Depends(get_api_key)])
async def list_flashcards():
    return {'message': 'TO DO'}


@router.get('/', dependencies=[Depends(get_api_key)])
async def get_flashcard():
    return {'message': 'TO DO'}


@router.post('/', dependencies=[Depends(get_api_key)])
async def create_flashcard():
    return {'message': 'TO DO'}


@router.put('/', dependencies=[Depends(get_api_key)])
async def update_flashcard():
    return {'message': 'TO DO'}


@router.delete('/', dependencies=[Depends(get_api_key)])
async def delete_flashcard():
    return {'message': 'TO DO'}
