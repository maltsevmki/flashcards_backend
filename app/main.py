from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.flashcards.router import router as flashcards_router
from app.core.config import settings


app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # change to mobile app's domain in prod!
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(flashcards_router, prefix='/flashcards', tags=['flashcards'])
