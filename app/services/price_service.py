"""
Сервис цен для бизнес-логики операций.

Обрабатывает операции с базой данных для записей о ценах.
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional, Protocol, runtime_checkable

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Database, get_database
from app.models import PriceRecord
from app.schemas import PriceRecordResponse
from clients.deribit_client import DeribitClient, PriceData

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger(__name__)


@runtime_checkable
class IPriceService(Protocol):
    """Протокол (интерфейс) сервиса цен."""

    async def save_price_data(self, price_data: PriceData) -> PriceRecord:
        ...

    async def fetch_and_save_all_prices(self) -> List[PriceRecord]:
        ...

    async def get_prices_by_ticker(
        self, ticker: str, limit: int, offset: int
    ) -> List[PriceRecordResponse]:
        ...

    async def get_latest_price(
        self, ticker: str
    ) -> Optional[PriceRecordResponse]:
        ...


class PriceService:
    """
    Сервис для операций с ценами.

    Предоставляет методы для сохранения и получения данных о ценах.
    Использует Dependency Injection для всех зависимостей.

    Attributes:
        database: Менеджер подключения к базе данных
        deribit_client: Клиент API Deribit
    """

    def __init__(
        self,
        database: Database | None = None,
        deribit_client: DeribitClient | None = None,
        settings: "Settings | None" = None,
    ) -> None:
        """
        Инициализация сервиса цен.

        Args:
            database: Менеджер БД. Если None - создаётся новый.
            deribit_client: Клиент Deribit. Если None - создаётся новый.
            settings: Настройки приложения.
        """
        self._database = database or get_database()
        self._deribit_client = deribit_client or DeribitClient()
        self._settings = settings

    @property
    def database(self) -> Database:
        """Получить менеджер базы данных."""
        return self._database

    @property
    def deribit_client(self) -> DeribitClient:
        """Получить клиент Deribit."""
        return self._deribit_client

    async def save_price_data(self, price_data: PriceData) -> PriceRecord:
        """
        Сохранить одну запись о цене в базу данных.

        Args:
            price_data: Данные о цене от клиента Deribit

        Returns:
            PriceRecord: Созданная запись в базе данных
        """
        async with self._database.get_session() as session:
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
        Получить все цены с Deribit и сохранить в базу данных.

        Returns:
            List[PriceRecord]: Список сохранённых записей
        """
        price_data_map = await self._deribit_client.fetch_all_prices()
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
        async with self._database.get_session() as session:
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
        self, ticker: str
    ) -> Optional[PriceRecordResponse]:
        """
        Получить последнюю цену для тикера.

        Args:
            ticker: Пара криптовалют

        Returns:
            Optional[PriceRecordResponse]: Последняя запись о цене или None
        """
        async with self._database.get_session() as session:
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


def get_price_service() -> PriceService:
    """
    Фабрика для получения инстанса сервиса цен.

    Returns:
        PriceService: Инстанс сервиса цен
    """
    return PriceService()
