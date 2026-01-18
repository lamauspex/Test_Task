"""Репозиторий для работы с записями о ценах в базе данных."""


from typing import Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import PriceRecord
from src.schemas import PriceRecordResponse


class PriceRepository:
    """Репозиторий для операций с записями о ценах."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория.

        Args:
            session: Асинхронная сессия базы данных
        """
        self._session = session

    async def save_price_data(
        self, ticker: str, price: float, timestamp: int
    ) -> PriceRecord:
        """
        Сохранить запись о цене в базу данных.

        Args:
            ticker: Пара криптовалют (например, 'btc_usd')
            price: Цена валюты
            timestamp: Временная метка в UNIX-формате

        Returns:
            PriceRecord: Созданная запись с присвоенным ID
        """
        record = PriceRecord(ticker=ticker, price=price, timestamp=timestamp)
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def get_prices_by_ticker(
        self,
        ticker: str,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[PriceRecordResponse]:
        """
        Получить все записи о ценах для указанного тикера.

        Args:
            ticker: Пара криптовалют (например, 'btc_usd')
            limit: Максимальное количество записей (по умолчанию 100)
            offset: Количество записей для пропуска

        Returns:
            Sequence[PriceRecordResponse]: Список записей, отсортированный
                по timestamp (новые первыми)
        """
        query = (
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        records = result.scalars().all()
        return [PriceRecordResponse.model_validate(r) for r in records]

    async def get_latest_price(self, ticker: str) -> PriceRecord | None:
        """
        Получить последнюю цену для указанного тикера.

        Args:
            ticker: Пара криптовалют (например, 'btc_usd')

        Returns:
            PriceRecord | None: Последняя запись о цене или None,
                если записей нет
        """
        query = (
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(PriceRecord.timestamp.desc())
            .limit(1)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_prices_by_date_range(
        self,
        ticker: str,
        start_date: int,
        end_date: int,
        limit: int = 100
    ) -> Sequence[PriceRecordResponse]:
        """
        Получить записи о ценах для тикера в указанном диапазоне дат.

        Args:
            ticker: Пара криптовалют (например, 'btc_usd')
            start_date: Начальная дата диапазона (UNIX timestamp)
            end_date: Конечная дата диапазона (UNIX timestamp)
            limit: Максимальное количество записей (по умолчанию 100)

        Returns:
            Sequence[PriceRecordResponse]: Список записей в диапазоне дат,
                отсортированный по timestamp (новые первыми)
        """
        query = (
            select(PriceRecord)
            .where(
                and_(
                    PriceRecord.ticker == ticker,
                    PriceRecord.timestamp >= start_date,
                    PriceRecord.timestamp <= end_date
                )
            )
            .order_by(PriceRecord.timestamp.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        records = result.scalars().all()
        return [PriceRecordResponse.model_validate(r) for r in records]
