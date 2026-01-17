"""Репозиторий для работы с записями о ценах в базе данных."""


from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import PriceRecord
from src.schemas import PriceRecordResponse
from src.middleware.exception_handler import get_business_logger


class PriceRepository:
    """Репозиторий для операций с записями о ценах."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория.

        Args:
            session: Асинхронная сессия базы данных
        """
        self._session = session
        self._business_logger = get_business_logger()

    async def save_price_data(
        self, ticker: str, price: float, timestamp: int
    ) -> PriceRecord:
        """
        Сохранить запись о цене в базу данных.

        Args:
            ticker: Пара криптовалют
            price: Цена
            timestamp: Временная метка

        Returns:
            PriceRecord: Созданная запись
        """
        record = PriceRecord(
            ticker=ticker,
            price=price,
            timestamp=timestamp
        )

        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)

        # Логирование через централизованный логгер
        self._business_logger.log_price_saved(
            ticker=record.ticker,
            price=record.price,
            timestamp=record.timestamp
        )

        return record

    async def get_prices_by_ticker(
        self,
        ticker: str,
        limit: int = 1000,
        offset: int = 0
    ) -> List[PriceRecordResponse]:
        """
        Получить записи о ценах для тикера в формате DTO.

        Args:
            ticker: Пара криптовалют
            limit: Максимальное количество записей
            offset: Количество записей для пропуска

        Returns:
            List[PriceRecordResponse]: Список DTO записей о ценах
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

    async def get_latest_price(self, ticker: str) -> Optional[PriceRecord]:
        """
        Получить последнюю цену для тикера.

        Args:
            ticker: Пара криптовалют

        Returns:
            Optional[PriceRecord]: Последняя запись о цене или None
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
        limit: int = 1000
    ) -> List[PriceRecordResponse]:
        """
        Получить записи о ценах для тикера в диапазоне дат в формате DTO.

        Args:
            ticker: Пара криптовалют
            start_date: Начальная дата (UNIX timestamp)
            end_date: Конечная дата (UNIX timestamp)
            limit: Максимальное количество записей

        Returns:
            List[PriceRecordResponse]: Список DTO записей о ценах
        """
        query = (
            select(PriceRecord)
            .where(
                PriceRecord.ticker == ticker,
                PriceRecord.timestamp >= start_date,
                PriceRecord.timestamp <= end_date
            )
            .order_by(PriceRecord.timestamp.desc())
            .limit(limit)
        )

        result = await self._session.execute(query)
        records = result.scalars().all()
        return [PriceRecordResponse.model_validate(r) for r in records]
