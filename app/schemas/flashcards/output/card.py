from pydantic import BaseModel


class FlashcardReviewOutput(BaseModel):
    card_id: int
    new_due: int
    new_ivl: int
    new_factor: int
    type_id: int
    queue_id: int
    reps: int
    lapses: int
    reviewed_at: int    # epoch (UTC) of review
    revlog_id: int


class FlashcardCreateOutput(BaseModel):
    card_id: int
    note_id: int
    deck: str
    front: str
    back: str
    tags: str
    created_at: str


class FlashcardListItemOutput(BaseModel):
    card_id: int
    note_id: int
    deck: str
    ord: int
    front: str
    back: str
    tags: str
    type_id: int
    queue_id: int
    due: int
    ivl: int


class FlashcardGetOutput(BaseModel):
    card_id: int
    note_id: int
    ord: int
    front: str
    back: str
    tags: str
    deck: str
    type_id: int
    queue_id: int
    due: int
    ivl: int
    factor: int
    reps: int
    lapses: int
    created_at: int


class FlashcardUpdateOutput(BaseModel):
    card_id: int
    note_id: int
    deck: str
    front: str
    back: str
    tags: str
    updated_at: int
    message: str
