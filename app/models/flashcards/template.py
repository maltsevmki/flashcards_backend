from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.flashcards.note import Notetype


class Template(SQLModel, table=True):
    ntid: int = Field(foreign_key='notetype.id', primary_key=True)
    ord: int = Field(primary_key=True)
    name: str
    mtime_secs: int
    usn: int
    config: bytes | None = None

    notetype: 'Notetype' = Relationship(back_populates='templates')


class FieldDef(SQLModel, table=True):
    ntid: int = Field(foreign_key='notetype.id', primary_key=True)
    ord: int = Field(primary_key=True)
    name: str
    config: bytes | None = None

    notetype: 'Notetype' = Relationship(back_populates='fields')
