from pydantic import BaseModel


class DeckGetOutput(BaseModel):
    deck_id: int
    name: str
    cards: int
    collection_id: int
    config_id: int
    mtime_secs: int


class DeckDeleteOutput(BaseModel):
    name: str
    deleted_cards: int
    deleted_notes: int
    message: str
    deleted_at: int


class DeckUpdateOutput(BaseModel):
    name: str
    updated_name: str | None
    updated_config_id: int | None
    message: str
    updated_at: int
