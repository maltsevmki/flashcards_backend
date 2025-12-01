from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import uuid4
from app.models.flashcards.card import Card
from app.models.flashcards.note import Note, Notetype
from app.models.flashcards.deck import Deck
from app.models.flashcards.template import Template
from app.models.flashcards.card import CardTypeEnum, QueueTypeEnum
from typing import List
from app.schemas.flashcards.input.card import (
    FlashcardCreateInput,
    FlashcardReviewInput,
    FlashcardListInput
)
from app.schemas.flashcards.output.card import (
    FlashcardReviewOutput,
    FlashcardListItemOutput
)
from app.models.flashcards.review_log import RevLog
from app.helper import get_user_localtime, anki_field_checksum


class Service:
    # Cards
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------

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

        mod = int(get_user_localtime(
            data.user_timezone_offset_minutes
        ).timestamp())
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

    @staticmethod
    async def list_cards(
        session: AsyncSession,
        data: FlashcardListInput
    ) -> List[FlashcardListItemOutput]:
        query = select(Card, Note, Deck).join(
            Note, Card.nid == Note.id
        ).join(Deck, Card.did == Deck.id)
        if data.deck_name is not None:
            query = query.where(Deck.name == data.deck_name)
        if data.type_id is not None:
            query = query.where(Card.type_id == data.type_id)
        query = query.offset(data.offset).limit(data.limit)
        results = await session.exec(query)
        cards: List[FlashcardListItemOutput] = []
        for card, note, deck in results.all():
            cards.append(FlashcardListItemOutput(
                card_id=card.id,
                note_id=note.id,
                deck=deck.name,
                ord=card.ord,
                front=note.flds.split('\x1f')[0],
                back=note.flds.split('\x1f')[1] if '\x1f' in note.flds else "",
                tags=note.tags.strip(),
                type_id=card.type_id,
                queue_id=card.queue_id,
                due=card.due,
                ivl=card.ivl
            ))

        return cards

    @staticmethod
    async def review_card(
        session: AsyncSession,
        data: FlashcardReviewInput
    ) -> FlashcardReviewOutput:
        card = (await session.exec(
            select(Card).where(Card.id == data.card_id)
        )).first()
        if not card:
            raise ValueError('Card not found')

        mod = int(get_user_localtime(
            user_timezone_offset_minutes=data.user_timezone_offset_minutes
        ).timestamp())
        last_ivl = card.ivl

        # Log review
        revlog_entry = RevLog(
            id=mod * 1000,
            cid=card.id,
            usn=0,
            ease=data.ease,
            ivl=last_ivl,
            lastIvl=last_ivl,
            factor=card.factor,
            time=data.review_time_ms,
            type=card.type_id,
        )
        session.add(revlog_entry)

        if card.type_id == CardTypeEnum.NEW.value:
            card.type_id = CardTypeEnum.LEARNING.value
            card.queue_id = QueueTypeEnum.LEARNING.value
            card.ivl = 0
            card.due = mod + 600  # next due in 10min for learning
        elif card.type_id == CardTypeEnum.LEARNING.value:
            card.type_id = CardTypeEnum.REVIEW.value
            card.queue_id = QueueTypeEnum.REVIEW.value
            card.ivl = 1
            card.due = mod + 86400  # due in 1 day (in seconds)
        elif card.type_id == CardTypeEnum.REVIEW.value:
            if data.ease == 1:
                card.lapses += 1
                card.ivl = 1
                card.due = mod + 86400
                card.factor = max(1300, card.factor - 200)
            else:
                if data.ease == 2:  # Hard
                    card.ivl = max(1, int(card.ivl * 1.2))
                    card.factor = max(1300, card.factor - 150)
                elif data.ease == 3:  # Good
                    card.ivl = max(1, int(card.ivl * card.factor / 1000))
                elif data.ease == 4:  # Easy
                    card.ivl = max(1, int(card.ivl * card.factor / 1000 * 1.3))
                card.due = mod + card.ivl * 86400
        elif card.type_id == CardTypeEnum.RELEARNING.value:
            card.type_id = CardTypeEnum.REVIEW.value
            card.queue_id = QueueTypeEnum.REVIEW.value
            card.ivl = 1  # reset to 1 day
            card.due = mod + 86400

        card.reps += 1
        card.mod = mod

        await session.commit()
        await session.refresh(card)

        return FlashcardReviewOutput(
            card_id=card.id,
            new_due=card.due,
            new_ivl=card.ivl,
            new_factor=card.factor,
            type_id=card.type_id,
            queue_id=card.queue_id,
            reps=card.reps,
            lapses=card.lapses,
            reviewed_at=mod,
            revlog_id=revlog_entry.id
        )

    # Decks
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
