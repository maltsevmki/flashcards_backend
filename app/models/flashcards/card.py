from app.models.flashcards.review_log import RevLog
from enum import IntEnum
from typing import TYPE_CHECKING, Optional, List
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.flashcards.note import Note
    from app.models.flashcards.deck import Deck


class CardTypeEnum(IntEnum):
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3

    @property
    def label(self):
        return {
            CardTypeEnum.NEW: 'new',
            CardTypeEnum.LEARNING: 'learning',
            CardTypeEnum.REVIEW: 'review',
            CardTypeEnum.RELEARNING: 'relearning'
        }[self]


class QueueTypeEnum(IntEnum):
    USER_BURIED = -3
    SCHED_BURIED = -2
    SUSPENDED = -1
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    IN_LEARNING = 3
    PREVIEW = 4

    @property
    def label(self):
        return {
            QueueTypeEnum.USER_BURIED: 'user buried',
            QueueTypeEnum.SCHED_BURIED: 'sched buried',
            QueueTypeEnum.SUSPENDED: 'suspended',
            QueueTypeEnum.NEW: 'new',
            QueueTypeEnum.LEARNING: 'learning',
            QueueTypeEnum.REVIEW: 'review',
            QueueTypeEnum.IN_LEARNING: 'in learning',
            QueueTypeEnum.PREVIEW: 'preview'
        }[self]


class CardType(SQLModel, table=True):
    '''
    Represents types, e.g. 0=new, 1=learning, 2=review, 3=relearning
    '''
    id: int = Field(default=None, primary_key=True)
    name: str

    cards: List['Card'] = Relationship(back_populates='type')  # reverse relation


class QueueType(SQLModel, table=True):
    '''
    Represents queue values.
    -- -3=user buried(In scheduler 2),
    -- -2=sched buried (In scheduler 2),
    -- -2=buried(In scheduler 1),
    -- -1=suspended,
    -- 0=new, 1=learning, 2=review (as for type)
    -- 3=in learning, next rev in at least a day after the previous review
    -- 4=preview
    '''
    id: int = Field(default=None, primary_key=True)
    name: str

    cards: List['Card'] = Relationship(back_populates='queue')


class Card(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nid: int = Field(foreign_key='note.id')
    did: int = Field(foreign_key='deck.id')
    ord: int
    mod: int
    usn: int

    type_id: int = Field(foreign_key='cardtype.id')
    queue_id: int = Field(foreign_key='queuetype.id')

    due: int
    ivl: int
    factor: int
    reps: int
    lapses: int
    left: int
    odue: int
    odid: int
    flags: int
    data: str

    note: 'Note' = Relationship(back_populates='cards')
    deck: 'Deck' = Relationship(back_populates='cards')
    type: Optional['CardType'] = Relationship(back_populates='cards')
    queue: Optional['QueueType'] = Relationship(back_populates='cards')
    revlogs: List['RevLog'] = Relationship(back_populates='card')
