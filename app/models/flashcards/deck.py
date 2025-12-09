from typing import TYPE_CHECKING, List
from sqlmodel import Field, SQLModel, Relationship


if TYPE_CHECKING:
    from app.models.flashcards.collection import Collection
    from app.models.flashcards.card import Card


class DeckConfig(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    mtime_secs: int
    usn: int
    config: bytes | None = None
    collection_id: int = Field(foreign_key='collection.id')

    collection: 'Collection' = Relationship(back_populates='deck_configs')
    decks: List['Deck'] = Relationship(back_populates='config')


class Deck(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    mtime_secs: int
    usn: int
    common: bytes | None = None
    kind: bytes | None = None
    collection_id: int = Field(foreign_key='collection.id')
    config_id: int = Field(foreign_key='deckconfig.id')

    collection: 'Collection' = Relationship(back_populates='decks')
    config: 'DeckConfig' = Relationship(back_populates='decks')
    cards: List['Card'] = Relationship(back_populates='deck')
