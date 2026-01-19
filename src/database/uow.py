"""Unit of Work паттерн для управления транзакциями."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .database import DatabaseManager
from repositories import PriceRepository


class UnitOfWork:
    """Unit of Work для управления транзакциями и репозиториями."""

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._database_manager = database_manager
        self._session: AsyncSession | None = None
        self._session_context = None
        self._prices: PriceRepository | None = None

    async def __aenter__(self) -> "UnitOfWork":
        """Вход в контекстный менеджер — открывает сессию."""
        # get_async_db_session() возвращает контекстный менеджер, входим в него
        self._session_context = self._database_manager.get_async_db_session()
        self._session = await self._session_context.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера — коммит или rollback"""

        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        # Закрываем контекстный менеджер сессии (он сам закроет сессию)
        if self._session_context is not None:
            await self._session_context.__aexit__(exc_type, exc_val, exc_tb)
        self._session = None
        self._session_context = None
        self._prices = None

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        if self._session:
            await self._session.rollback()

    @property
    def prices(self) -> PriceRepository:
        """Получить репозиторий цен (lazy initialization)"""

        if self._prices is None:
            if self._session is None:
                raise RuntimeError(
                    "UnitOfWork not initialized. Use 'async with'")
            self._prices = PriceRepository(self._session)
        return self._prices


@asynccontextmanager
async def get_uow(
    database_manager: DatabaseManager,
) -> AsyncGenerator[UnitOfWork, None]:
    """Фабрика UnitOfWork для использования в FastAPI Depends"""

    async with UnitOfWork(database_manager) as uow:
        yield uow
