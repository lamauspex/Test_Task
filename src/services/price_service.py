"""
Сервис цен для бизнес-логики операций.

Обрабатывает операции с базой данных для записей о ценах через репозиторий.
"""

from typing import List, Optional

from src.config import settings
from src.repositories import PriceRepository
from src.schemas import PriceRecordResponse
from src.database import DatabaseManager
from src.middleware.exception_handler import get_business_logger
from clients.deribit_client import DeribitClient, PriceData


class PriceService:
    """
    Сервис для операций с ценами.

    Предоставляет методы для сохранения и получения данных о ценах.
    Использует Repository pattern для доступа к данным.

    Attributes:
        database_manager: Менеджер подключения к базе данных
        deribit_client: Клиент API Deribit
        business_logger: Логгер для бизнес-операций
    """

    def __init__(
        self,
        database_manager: DatabaseManager | None = None,
        deribit_client: DeribitClient | None = None,
        business_logger=None,
    ) -> None:
        """
        Инициализация сервиса цен.

        Args:
            database_manager: Менеджер БД. Если None - используется глобальный.
            deribit_client: Клиент Deribit. Если None - создаётся новый.
            business_logger: Логгер бизнес-операций. Если None создаётся новый.
        """

        self._database_manager = database_manager or DatabaseManager(
            settings.database.get_database_url()
        )
        self._deribit_client = deribit_client or DeribitClient()
        self._business_logger = business_logger or get_business_logger()

    @property
    def database_manager(self) -> DatabaseManager:
        """Получить менеджер базы данных."""
        return self._database_manager

    @property
    def deribit_client(self) -> DeribitClient:
        """Получить клиент Deribit."""
        return self._deribit_client

    async def save_price_data(self, price_data: PriceData) -> None:
        """
        Сохранить данные о цене через репозиторий.

        Args:
            price_data: Данные о цене от клиента Deribit
        """

        async with self._database_manager.get_async_db_session() as session:
            repository = PriceRepository(session)
            record = await repository.save_price_data(
                ticker=price_data.ticker,
                price=price_data.price,
                timestamp=price_data.timestamp
            )

            # Логирование через централизованный логгер
            self._business_logger.log_price_saved(
                ticker=record.ticker,
                price=record.price,
                timestamp=record.timestamp
            )

    async def fetch_and_save_all_prices(self) -> List[str]:
        """
        Получить все цены с Deribit и сохранить в базу данных.

        Returns:
            List[str]: Список тикеров сохранённых записей
        """

        price_data_map = await self._deribit_client.fetch_all_prices()
        saved_tickers = []

        async with self._database_manager.get_async_db_session() as session:
            repository = PriceRepository(session)

            for ticker, price_data in price_data_map.items():
                await repository.save_price_data(
                    ticker=price_data.ticker,
                    price=price_data.price,
                    timestamp=price_data.timestamp
                )
                saved_tickers.append(ticker)

        # Логирование через централизованный логгер
        self._business_logger.log_prices_saved(saved_tickers)

        return saved_tickers

    async def get_prices_by_ticker(
        self,
        ticker: str,
        limit: int = 1000,
        offset: int = 0
    ) -> List:
        """
        Получить записи о ценах для тикера через репозиторий.

        Args:
            ticker: Пара криптовалют
            limit: Максимальное количество возвращаемых записей
            offset: Количество записей для пропуска

        Returns:
            List: Список записей о ценах в формате DTO
        """

        async with self._database_manager.get_async_db_session() as session:
            repository = PriceRepository(session)
            return await repository.get_prices_by_ticker(
                ticker=ticker,
                limit=limit,
                offset=offset
            )

    async def get_latest_price(
        self, ticker: str
    ) -> Optional:
        """
        Получить последнюю цену для тикера через репозиторий.

        Args:
            ticker: Пара криптовалют

        Returns:
            Optional: Последняя запись о цене в формате DTO или None
        """

        async with self._database_manager.get_async_db_session() as session:
            repository = PriceRepository(session)
            record = await repository.get_latest_price(ticker)

            if record:
                return PriceRecordResponse.model_validate(record)
            return None

    async def get_prices_by_date_range(
        self,
        ticker: str,
        start_date: int,
        end_date: int,
        limit: int = 1000
    ) -> List:
        """
        Получить записи о ценах для тикера в диапазоне дат через репозиторий.

        Args:
            ticker: Пара криптовалют
            start_date: Начальная дата (UNIX timestamp)
            end_date: Конечная дата (UNIX timestamp)
            limit: Максимальное количество записей

        Returns:
            List: Список записей о ценах в формате DTO
        """

        async with self._database_manager.get_async_db_session() as session:
            repository = PriceRepository(session)
            return await repository.get_prices_by_date_range(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )


def get_price_service() -> PriceService:
    """
    Фабрика для получения инстанса сервиса цен.

    Returns:
        PriceService: Инстанс сервиса цен
    """
    return PriceService()
