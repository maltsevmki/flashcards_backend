from typing import Optional
from pydantic import BaseModel


class FlashcardListInput(BaseModel):
    deck_name: Optional[str] = None
    type_id: Optional[int] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0


class FlashcardReviewInput(BaseModel):
    card_id: int
    ease: int  # 1=Again, 2=Hard, 3=Good, 4=Easy
    review_time_ms: int
    user_timezone_offset_minutes: Optional[int] = 0


class FlashcardCreateInput(BaseModel):
    type_name: str
    deck_name: str
    front: str
    back: str
    tags: Optional[str] = ''
    user_timezone_offset_minutes: Optional[int] = 0


class FlashcardUpdateInput(BaseModel):
    card_id: int
    front: Optional[str] = None
    back: Optional[str] = None
    tags: Optional[str] = None
    user_timezone_offset_minutes: Optional[int] = 0
