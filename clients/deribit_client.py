"""
Клиент API Deribit.

"""
import logging
from typing import Dict

from .deribit_http_client import DeribitHttpClient
from .deribit_mapper import DeribitMapper, deribit_mapper
from .deribit_parser import PriceData, DeribitParser, deribit_parser
from src.exceptions.exceptions import DeribitClientError


logger = logging.getLogger(__name__)


class IDeribitClient:
    """Интерфейс клиента Deribit."""

    async def fetch_price(self, ticker: str) -> PriceData:
        """Получить цену для тикера."""
        ...

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """Получить все цены."""
        ...


class DeribitClient(IDeribitClient):
    """
    Клиент для API криптобиржи Deribit.

    Компонует:
    - DeribitHttpClient: управление HTTP-сессией и запросами
    - DeribitMapper: маппинг тикеров
    - DeribitParser: парсинг ответа API

    Attributes:
        http_client: HTTP-клиент для запросов
        mapper: Маппер тикеров
        parser: Парсер ответа
    """

    def __init__(
        self,
        http_client: DeribitHttpClient | None = None,
        mapper: DeribitMapper | None = None,
        parser: DeribitParser | None = None,
    ) -> None:
        """ Инициализация клиента Deribit """

        self._http_client = http_client or DeribitHttpClient()
        self._mapper = mapper or deribit_mapper
        self._parser = parser or deribit_parser

    async def fetch_price(self, ticker: str) -> PriceData:
        """ Получить цену для тикера """

        # Валидация тикера через маппер
        currency = self._mapper.get_currency(ticker)
        if not currency:
            raise DeribitClientError(f"Unknown ticker: {ticker}")

        # Deribit API требует index_name (например: btc_usd)
        index_name = f"{currency.lower()}_usd"

        # Выполнение HTTP-запроса
        async with self._http_client:
            response = await self._http_client.request(
                method="GET",
                endpoint="get_index_price",
                params={"index_name": index_name}
            )

        # Парсинг ответа
        return self._parser.parse_price_response(response, ticker)

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """ Получить цены для всех отслеживаемых валют """

        tickers = ["btc_usd", "eth_usd"]
        prices = {}

        async with self:
            for ticker in tickers:
                try:
                    price_data = await self.fetch_price(ticker)
                    prices[ticker] = price_data
                    logger.info(
                        f"Fetched price for {ticker}: {price_data.price}")
                except DeribitClientError as e:
                    logger.error(f"Failed to fetch {ticker}: {e}")
                    # Продолжаем с другими тикерами даже при ошибке одного

        return prices

    async def get_available_index_names(self) -> list:
        """Получить список доступных индексов (для отладки)."""
        async with self._http_client:
            response = await self._http_client.request(
                method="GET",
                endpoint="get_index_price_names",
                params={}
            )
        return response.get("result", {}).get("index_names", [])

    async def close(self) -> None:
        """Закрыть HTTP-сессию."""
        await self._http_client.close()

    async def __aenter__(self) -> "DeribitClient":
        """Контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        await self.close()


# Экземпляры по умолчанию для внедрения зависимостей
default_http_client = DeribitHttpClient()
default_mapper = deribit_mapper
default_parser = deribit_parser
