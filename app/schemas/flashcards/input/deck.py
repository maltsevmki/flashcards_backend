from pydantic import BaseModel


class DeckCreateInput(BaseModel):
    name: str


class DeckListOutput(BaseModel):
    id: int
    name: str
