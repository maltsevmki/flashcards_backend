from pydantic import BaseModel


class FlashcardCreateOutput(BaseModel):
    card_id: int
    note_id: int
    deck: str
    front: str
    back: str
    tags: str
    created_at: str
