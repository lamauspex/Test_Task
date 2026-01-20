"""Конфигурация pytest для тестов с SQLite in-memory."""

from src.models.models_base import Base
from src.database.database import DatabaseManager
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from dotenv import load_dotenv
import pytest_asyncio
import pytest
from typing import AsyncGenerator
import sys
from pathlib import Path

# Добавляем src/ в PYTHONPATH для импортов (ДО импортов из src!)
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


# Загружаем переменные окружения для тестов (опционально)
dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path, override=True)


# URL для SQLite in-memory
SQLITE_TEST_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Фикстура для управления циклом событий"""

    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Создаём движок SQLite in-memory для тестов"""

    engine = create_async_engine(
        SQLITE_TEST_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Создаём таблицы и очищаем после каждого теста"""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_session(
    test_engine: AsyncEngine,
    test_db
) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для получения сессии БД в тестах"""

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_uow(test_engine: AsyncEngine) -> AsyncGenerator:
    """Фикстура для UnitOfWork в тестах."""
    from src.database.uow import UnitOfWork
    from src.database.database import DatabaseManager

    db_manager = DatabaseManager(SQLITE_TEST_URL)
    async with UnitOfWork(db_manager) as uow:
        yield uow


@pytest.fixture
def mock_db_manager(test_engine: AsyncEngine) -> DatabaseManager:
    """Фикстура для подмены DatabaseManager в тестах."""
    return DatabaseManager(SQLITE_TEST_URL)
