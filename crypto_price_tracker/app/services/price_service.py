"""
Сервис цен для бизнес-логики операций.

Обрабатывает операции с базой данных для записей о ценах.
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, func

from app.database import database
from app.models import PriceRecord
from app.schemas import PriceRecordResponse
from clients.deribit_client import PriceData, deribit_client

logger = logging.getLogger(__name__)


class PriceService:
    """
    Сервис для операций с ценами
    Предоставляет методы для сохранения и получения данных о ценах
    """

    def __init__(self) -> None:
        """ Инициализация сервиса цен """
        self._client = deribit_client

    async def save_price_data(self, price_data: PriceData) -> PriceRecord:
        """
        Сохранить одну запись о цене в базу данных

        Args:
            price_data: Данные о цене от клиента Deribit

        Returns:
            PriceRecord: Созданная запись в базе данных
        """
        async with database.get_session() as session:
            record = PriceRecord(
                ticker=price_data.ticker,
                price=price_data.price,
                timestamp=price_data.timestamp
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)

            logger.debug(
                f"Сохранена запись о цене: {record.ticker} = {record.price} "
                f"@ {datetime.fromtimestamp(record.timestamp)}"
            )

            return record

    async def fetch_and_save_all_prices(self) -> List[PriceRecord]:
        """
        Получить все цены с Deribit и сохранить в базу данных

        Returns:
            List[PriceRecord]: Список сохранённых записей
        """
        price_data_map = await self._client.fetch_all_prices()
        saved_records = []

        for ticker, price_data in price_data_map.items():
            record = await self.save_price_data(price_data)
            saved_records.append(record)

        logger.info(
            f"Сохранено {len(saved_records)} записей о ценах в базу данных"
        )

        return saved_records

    async def get_prices_by_ticker(
        self,
        ticker: str,
        limit: int = 1000,
        offset: int = 0
    ) -> List[PriceRecordResponse]:
        """
        Получить все записи о ценах для тикера.

        Args:
            ticker: Пара криптовалют
            limit: Максимальное количество возвращаемых записей
            offset: Количество записей для пропуска

        Returns:
            List[PriceRecordResponse]: Список записей о ценах
        """
        async with database.get_session() as session:
            query = (
                select(PriceRecord)
                .where(PriceRecord.ticker == ticker)
                .order_by(PriceRecord.timestamp.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(query)
            records = result.scalars().all()

            return [PriceRecordResponse.model_validate(r) for r in records]

    async def get_latest_price(
        self,
        ticker: str
    ) -> Optional[PriceRecordResponse]:
        """
        Получить последнюю цену для тикера

        Args:
            ticker: Пара криптовалют

        Returns:
            Optional[PriceRecordResponse]: Последняя запись о цене или None
        """
        async with database.get_session() as session:
            query = (
                select(PriceRecord)
                .where(PriceRecord.ticker == ticker)
                .order_by(PriceRecord.timestamp.desc())
                .limit(1)
            )

            result = await session.execute(query)
            record = result.scalar_one_or_none()

            if record:
                return PriceRecordResponse.model_validate(record)
            return None

    async def get_prices_by_date_range(
        self,
        ticker: str,
        start_date: int,
        end_date: int,
        limit: int = 1000
    ) -> PriceRecordResponse:
        """
        Получить записи о ценах в диапазоне дат

        Args:
            ticker: Пара криптовалют
            start_date: Начальный UNIX timestamp
            end_date: Конечный UNIX timestamp
            limit: Максимальное количество возвращаемых записей

        Returns:
            PriceRecordResponse: Ответ с записями о ценах
        """
        async with database.get_session() as session:
            # Запрос подсчёта
            count_query = (
                select(func.count(PriceRecord.id))
                .where(
                    PriceRecord.ticker == ticker,
                    PriceRecord.timestamp >= start_date,
                    PriceRecord.timestamp <= end_date
                )
            )
            count_result = await session.execute(count_query)
            total_count = count_result.scalar()

            # Запрос данных
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

            result = await session.execute(query)
            records = result.scalars().all()

            # Построение ответа с последней записью для информации заголовка
            latest_record = records[0] if records else None

            return PriceRecordResponse.model_validate(latest_record) \
                if latest_record else None


# Синглтон экземпляр для использования в приложении
price_service = PriceService()
