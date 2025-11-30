from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import uuid4
from app.models.flashcards.card import Card
from app.models.flashcards.note import Note, Notetype
from app.models.flashcards.deck import Deck
from app.models.flashcards.template import Template
from app.models.flashcards.card import CardTypeEnum, QueueTypeEnum
from app.schemas.flashcards.input.card import FlashcardCreateInput
from app.helper import get_modification_epoch, anki_field_checksum


class CardService:
    @staticmethod
    async def create_card(
        session: AsyncSession,
        data: FlashcardCreateInput
    ) -> Card:
        deck = (await session.exec(
            select(Deck).where(Deck.name == data.deck_name))
        ).first()
        if not deck:
            raise ValueError(f'Deck with name {data.deck_name} not found.')

        mod = get_modification_epoch(data.user_timezone_offset_minutes)
        notetype = (await session.exec(
            select(Notetype).where(Notetype.name == data.type_name)
        )).first()
        if not notetype:
            raise ValueError(f'No notetype found for {data.type_name}')

        templates = (await session.exec(
            select(Template).where(Template.ntid == notetype.id)
        )).all()

        csum = anki_field_checksum(data.front)
        existing_note = (await session.exec(
            select(Note)
            .where(Note.csum == csum)
            .where(Note.mid == notetype.id)
        )).first()
        if existing_note:
            raise ValueError(
                'Note with same sort field already exists in this notetype.'
            )

        note = Note(
            guid=uuid4().hex,
            mid=notetype.id,
            mod=mod,
            usn=0,
            tags=f' {data.tags.strip()} ' if data.tags else '',
            flds=f'{data.front}\x1f{data.back}',
            sfld=data.front,
            csum=csum,
            flags=0,
            data=''
        )

        session.add(note)
        await session.commit()
        await session.refresh(note)

        created_cards = []
        for t in templates:
            existing_dues = await session.exec(
                select(Card.due)
                .where(Card.did == deck.id)
                .where(Card.type_id == CardTypeEnum.NEW.value)
                .where(Card.queue_id == QueueTypeEnum.NEW.value)
            )
            max_due = max(existing_dues.all() or [0])

            card = Card(
                nid=note.id,
                did=deck.id,
                ord=t.ord,
                mod=mod,
                usn=0,
                type_id=CardTypeEnum.NEW.value,
                queue_id=QueueTypeEnum.NEW.value,
                due=max_due + 1,
                ivl=0,
                factor=2500,
                reps=0,
                lapses=0,
                left=0,
                odue=0,
                odid=0,
                flags=0,
                data=''
            )
            session.add(card)
            created_cards.append(card)

        await session.commit()
        await session.refresh(card)

        return card
