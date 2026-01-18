"""
Менеджер подключения к базе данных.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from src.config import settings


class DatabaseManager:
    """Менеджер базы данных для управления подключением."""

    def __init__(self, database_url: str):
        """
        Инициализация менеджера БД.

        Args:
            database_url: URL для подключения к БД
        """
        self.engine = create_async_engine(database_url)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_async_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Получить асинхронную сессию БД.

        Yields:
            AsyncSession: Активная сессия базы данных
        """
        async with self.session_factory() as session:
            yield session


# Глобальный экземпляр для использования в приложении
database_manager = DatabaseManager(settings.database.get_database_url())


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Глобальная функция для получения сессии БД.

    Используется для FastAPI Depends.

    Yields:
        AsyncSession: Активная сессия базы данных
    """
    async with database_manager.session_factory() as session:
        yield session
