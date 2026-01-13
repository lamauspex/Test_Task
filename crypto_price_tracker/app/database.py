"""
Управление подключением к базе данных.

Предоставляет асинхронный движок и фабрику сессий.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import close_all_sessions

from app.config import get_settings
from app.models import Base


class Database:
    """
    Менеджер подключения к базе данных
    Управляет асинхронным движком и фабрикой сессий для PostgreSQL
    """

    def __init__(self) -> None:
        """ Инициализация базы данных с настройками """

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def init(self) -> None:
        """
        Инициализация подключения к базе данных
        Создаёт асинхронный движок и фабрику сессий на основе конфигурации
        """
        settings = get_settings()

        self._engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def create_tables(self) -> None:
        """
        Создание всех таблиц базы данных
        Использует метаданные SQLAlchemy для создания таблиц,
        если они не существуют
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Получить асинхронную сессию базы данных

        Yields:
            AsyncSession: Сессия базы данных для операций

        Пример использования:
            async with db.get_session() as session:
                # выполнить операции с базой данных
        """
        if not self._session_factory:
            raise RuntimeError(
                "База данных не инициализирована. Сначала вызовите init().")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        """
        Закрыть подключения к базе данных
        Правильно закрывает все соединения и освобождает ресурсы
        """
        if self._engine:
            await self._engine.dispose()
            close_all_sessions()
            self._engine = None
            self._session_factory = None


# Синглтон экземпляр для использования в приложении
database = Database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI зависимость для сессии базы данных

    Yields:
        AsyncSession: Сессия базы данных

    Пример использования:
        @app.get("/")
        async def endpoint(session: AsyncSession = Depends(get_db)):
            # использовать session
    """
    async with database.get_session() as session:
        yield session
