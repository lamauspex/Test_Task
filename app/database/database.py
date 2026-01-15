"""
Управление подключением к базе данных.

Предоставляет асинхронный движок и фабрику сессий.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import close_all_sessions

from app.models.models_base import Base

if TYPE_CHECKING:
    from app.config.config import Settings


class Database:
    """
    Менеджер подключения к базе данных
    Управляет асинхронным движком и фабрикой сессий для PostgreSQL

    Example:
        db = Database(settings)
        await db.init()
        async with db.get_session() as session:
            # работа с базой
    """

    def __init__(self, settings: "Settings | None" = None) -> None:
        """
        Инициализация менеджера базы данных.

        Args:
            settings: Настройки приложения.
            Если None - используются по умолчанию.
        """
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._settings = settings

    async def init(self, database_url: str | None = None) -> None:
        """
        Инициализация подключения к базе данных.

        Args:
            database_url: URL подключения. Если None - берётся из настроек.
        """
        from app.config.config import get_settings

        settings = self._settings or get_settings()
        url = database_url or settings.database_url

        self._engine = create_async_engine(
            url,
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
        """Создание всех таблиц базы данных."""
        if not self._engine:
            raise RuntimeError("База данных не инициализирована")

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Получить асинхронную сессию базы данных.

        Yields:
            AsyncSession: Сессия базы данных для операций

        Raises:
            RuntimeError: Если база данных не инициализирована
        """
        if not self._session_factory:
            raise RuntimeError(
                "База данных не инициализирована. Сначала вызовите init()."
            )

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
        """Закрыть подключения к базе данных."""
        if self._engine:
            await self._engine.dispose()
            close_all_sessions()
            self._engine = None
            self._session_factory = None


# Функция для FastAPI Depends - создаёт новый инстанс
def get_database() -> Database:
    """
    Фабрика для получения инстанса базы данных.

    Returns:
        Database: Инстанс менеджера базы данных
    """
    return Database()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI зависимость для сессии базы данных.

    Yields:
        AsyncSession: Сессия базы данных

    Example:
        @app.get("/")
        async def endpoint(session: AsyncSession = Depends(get_db)):
            ...
    """
    db = get_database()
    async with db.get_session() as session:
        yield session
