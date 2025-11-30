from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.flashcards.router import router as flashcards_router
from app.core.config import settings
from app.db import init_db, async_session
from app.models.flashcards.card import CardType, QueueType, CardTypeEnum, QueueTypeEnum
from sqlmodel import select
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as session:
        existing_types = await session.exec(select(CardType))
        if not existing_types.first():
            session.add_all([
                CardType(id=ct.value, name=ct.label)
                for ct in CardTypeEnum
            ])
            session.add_all([
                QueueType(id=qt.value, name=qt.label)
                for qt in QueueTypeEnum
            ])
            await session.commit()
    yield

app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(flashcards_router, prefix='/flashcards', tags=['flashcards'])
