"""
Shared fixtures for FlashCard API tests.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.models.flashcards.card import Card, CardType, QueueType, CardTypeEnum, QueueTypeEnum
from app.models.flashcards.deck import Deck, DeckConfig
from app.models.flashcards.note import Note, Notetype
from app.models.flashcards.collection import Collection
from app.models.flashcards.template import Template


# Use SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Use a smaller timestamp to avoid SQLite integer overflow
TEST_TIMESTAMP = 1700000000  # Fixed timestamp for testing


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def seeded_session(test_session):
    """
    Create a test session with seed data.
    """
    session = test_session
    mtime = TEST_TIMESTAMP

    # Create CardTypes
    for ct in CardTypeEnum:
        session.add(CardType(id=ct.value, name=ct.label))

    # Create QueueTypes
    for qt in QueueTypeEnum:
        session.add(QueueType(id=qt.value, name=qt.label))

    # Create Collection
    collection = Collection(
        id=1,
        crt=mtime,
        mod=mtime,
        ver=11,
        usn=0
    )
    session.add(collection)

    # Create DeckConfig
    deck_config = DeckConfig(
        id=1,
        name="Default",
        mtime_secs=mtime,
        usn=0,
        config=None,
        collection_id=1
    )
    session.add(deck_config)

    # Create Notetype
    notetype = Notetype(
        id=1,
        name="Basic",
        mtime_secs=mtime,
        usn=0,
        config=None,
        collection_id=1
    )
    session.add(notetype)

    await session.commit()

    # Create Template (composite primary key: ntid + ord)
    template = Template(
        ntid=1,
        ord=0,
        name="Card 1",
        mtime_secs=mtime,
        usn=0,
        config=None
    )
    session.add(template)

    # Create a sample Deck
    deck = Deck(
        id=1,
        name="Test Deck",
        mtime_secs=mtime,
        usn=0,
        collection_id=1,
        config_id=1
    )
    session.add(deck)

    await session.commit()

    yield session


@pytest.fixture
async def seeded_session_with_cards(seeded_session):
    """
    Create a session with seed data plus sample cards for testing.
    """
    session = seeded_session
    mod = TEST_TIMESTAMP

    # Create sample notes and cards
    notes_data = [
        ("What is Python?", "A programming language", "programming python"),
        ("What is FastAPI?", "A modern Python web framework", "python fastapi"),
        ("What is SQLModel?", "SQL databases with Python types", "python database"),
        ("What is pytest?", "A testing framework for Python", "python testing"),
        ("What is Docker?", "A containerization platform", "devops docker"),
    ]

    for i, (front, back, tags) in enumerate(notes_data, start=1):
        note = Note(
            id=i,
            guid=f"test-guid-{i}",
            mid=1,
            mod=mod,
            usn=0,
            tags=f" {tags} ",
            flds=f"{front}\x1f{back}",
            sfld=front,
            csum=i * 1000,
            flags=0,
            data=""
        )
        session.add(note)

        card = Card(
            id=i,
            nid=i,
            did=1,
            ord=0,
            mod=mod,
            usn=0,
            type_id=CardTypeEnum.NEW.value,
            queue_id=QueueTypeEnum.NEW.value,
            due=i,
            ivl=0,
            factor=2500,
            reps=0,
            lapses=0,
            left=0,
            odue=0,
            odid=0,
            flags=0,
            data=""
        )
        session.add(card)

    await session.commit()

    yield session


@pytest.fixture
def api_key_headers():
    """Headers with valid API key for authenticated requests."""
    return {"X-API-KEY": "test-secret-token"}


@pytest.fixture
def invalid_api_key_headers():
    """Headers with invalid API key."""
    return {"X-API-KEY": "invalid-key"}


# For integration tests - simplified client without complex mocking
@pytest.fixture
async def async_client():
    """Create an async test client for basic endpoint testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_client_with_cards():
    """Create an async test client for testing with cards."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
