"""Unit of Work паттерн для управления транзакциями."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import PriceRepository


class UnitOfWork:
    """Unit of Work для управления транзакциями и репозиториями."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session
        self._prices: Optional[PriceRepository] = None

    async def __aenter__(self) -> "UnitOfWork":
        """Вход в контекстный менеджер."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера — коммит или rollback."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        await self._session.rollback()

    @property
    def prices(self) -> PriceRepository:
        """Получить репозиторий цен (lazy initialization)"""

        if self._prices is None:
            self._prices = PriceRepository(self._session)
        return self._prices
