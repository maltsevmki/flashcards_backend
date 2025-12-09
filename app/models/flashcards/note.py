from app.models.flashcards.collection import Collection
from app.models.flashcards.template import Template, FieldDef
from typing import TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.flashcards.card import Card


class Notetype(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    mtime_secs: int
    usn: int
    config: bytes | None = None
    collection_id: int = Field(foreign_key='collection.id')

    collection: 'Collection' = Relationship(back_populates='notetypes')
    templates: List['Template'] = Relationship(back_populates='notetype')
    fields: List['FieldDef'] = Relationship(back_populates='notetype')
    notes: List['Note'] = Relationship(back_populates='notetype')


class Note(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    guid: str
    mid: int = Field(foreign_key='notetype.id')
    mod: int
    usn: int
    tags: str
    flds: str
    sfld: int
    csum: int
    flags: int
    data: str

    notetype: 'Notetype' = Relationship(back_populates='notes')
    cards: List['Card'] = Relationship(back_populates='note')
