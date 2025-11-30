from typing import Optional
from pydantic import BaseModel


class FlashcardCreateInput(BaseModel):
    type_name: str
    deck_name: str
    front: str
    back: str
    tags: Optional[str] = ''
    user_timezone_offset_minutes: Optional[int] = 0
