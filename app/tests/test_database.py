import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database.database import Base
from app.database.crud.users import UserRepository
from app.database.crud.messages import MessageRepository

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Creates a new database session for each test"""
    async with TestingSessionLocal() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield session
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def user_repo(db_session: AsyncSession):
    """Provides an instance of UserRepository for tests"""
    return UserRepository(db_session)

@pytest_asyncio.fixture(scope="function")
async def message_repo(db_session: AsyncSession):
    """Provides an instance of MessageRepository for tests"""
    return MessageRepository(db_session)
