from typing import List
from pydantic import BaseModel


class DeckCreateOutput(BaseModel):
    id: int
    name: str


class DeckListOutput(BaseModel):
    decks: List[DeckCreateOutput]
