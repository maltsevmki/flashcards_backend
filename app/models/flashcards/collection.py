from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.flashcards.note import Notetype
    from app.models.flashcards.deck import Deck
    from app.models.flashcards.deck import DeckConfig


class Collection(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    crt: int
    mod: int
    ver: int
    usn: int

    notetypes: List['Notetype'] = Relationship(back_populates='collection')
    decks: List['Deck'] = Relationship(back_populates='collection')
    deck_configs: List['DeckConfig'] = Relationship(back_populates='collection')
