import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.app.db.base import Base
from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.main import app
from backend.app.models.conversation import Conversation
from backend.app.models.user import User

# 1. Setup an isolated, in-memory SQLite database just for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # <--- Add this!
)


@pytest.fixture(autouse=True)
async def setup_db():
    """Creates the tables before each test and drops them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """A test client that overrides the real database with our test database."""
    app.dependency_overrides[get_db] = lambda: db_session
    # ASGITransport allows testing FastAPI directly without spinning up a real server
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c
    app.dependency_overrides.clear()


# 2. Setup Mock Users


@pytest.fixture
def mock_user_1():
    return User(id=1, email="alice@example.com", is_active=True)


@pytest.fixture
def mock_user_2():
    return User(id=2, email="bob@example.com", is_active=True)


# 3. Setup Mock Clients (Dependency Overrides for Auth)


@pytest.fixture
async def authorized_client(client, mock_user_1):
    """A client simulating Alice being logged in."""
    app.dependency_overrides[get_current_user] = lambda: mock_user_1
    yield client


@pytest.fixture
async def alice_client(client, mock_user_2):
    """A client simulating Bob being logged in (used to test resource hiding)."""
    app.dependency_overrides[get_current_user] = lambda: mock_user_2
    yield client


# 4. Setup Mock Data


@pytest.fixture
async def test_conversation_id(db_session, mock_user_1):
    conv = Conversation(title="Alice's Chat", user_id=mock_user_1.id)
    db_session.add(conv)
    await db_session.commit()
    return conv.id


@pytest.fixture
async def bob_conversation_id(db_session, mock_user_1):
    conv = Conversation(title="Bob's Secret Chat", user_id=mock_user_1.id)
    db_session.add(conv)
    await db_session.commit()
    return conv.id
