from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.flashcards.card import Card


class RevLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    cid: int = Field(foreign_key='card.id')
    usn: int
    ease: int
    ivl: int
    lastIvl: int
    factor: int
    time: int
    type: int

    card: 'Card' = Relationship(back_populates='revlogs')
