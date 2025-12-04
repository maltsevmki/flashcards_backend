from pydantic import BaseModel
from typing import Optional


class DeckCreateInput(BaseModel):
    name: str


class DeckGetInput(BaseModel):
    deck_id: int


class DeckDeleteInput(BaseModel):
    deck_id: int
    user_timezone_offset_minutes: Optional[int] = 0


class DeckUpdateInput(BaseModel):
    deck_id: int                      # Current deck id
    new_name: str | None = None    # New name (optional)
    config_id: int | None = None
    user_timezone_offset_minutes: Optional[int] = 0
