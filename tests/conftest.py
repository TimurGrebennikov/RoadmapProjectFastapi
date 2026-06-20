from collections.abc import AsyncGenerator

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.db.models import ParcelType
from src.domain.repositories.parcel_repository import ParcelRepository
from src.domain.services.parcel import ParcelService
from src.main import app

# In-memory SQLite. StaticPool гарантирует, что все сессии используют
# одно и то же соединение, поэтому данные сохраняются между сессиями.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Создать тестовый async-движок и схему БД, удалить их после теста."""
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with test_engine.begin() as conn: # type: ignore
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    async with test_engine.begin() as conn: # type: ignore
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Фабрика async-сессий, привязанная к тестовому движку."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Отдельная async-сессия БД для прямых тестов репозитория/сервиса."""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def parcel_types(
    session_factory: async_sessionmaker[AsyncSession],
) -> list[ParcelType]:
    """Заполнить БД базовыми типами посылок и вернуть их."""
    async with session_factory() as session:
        types = [
            ParcelType(name="одежда"),
            ParcelType(name="электроника"),
            ParcelType(name="разное"),
        ]
        session.add_all(types)
        await session.commit()
        for parcel_type in types:
            await session.refresh(parcel_type)
        return types


@pytest_asyncio.fixture
async def repository(db_session: AsyncSession) -> ParcelRepository:
    """Экземпляр ParcelRepository, использующий тестовую сессию."""
    return ParcelRepository(db_session)


@pytest_asyncio.fixture
async def service(repository: ParcelRepository) -> ParcelService:
    """Экземпляр ParcelService поверх тестового репозитория."""
    return ParcelService(repository)


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
    parcel_types: list[ParcelType],
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP-клиент с переопределённой зависимостью БД.

    Зависимость ``get_db`` переопределяется на тестовую in-memory БД.
    Фикстура ``parcel_types`` гарантирует наличие справочника типов.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()