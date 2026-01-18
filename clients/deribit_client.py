""" Клиент API Deribit с использованием aiohttp для асинхронных HTTP-запросов.

Получает индексные цены для BTC/USD и ETH/USD.
Документация: https://docs.deribit.com/
"""
import logging
from dataclasses import dataclass
from typing import Dict

import aiohttp

from src.config import settings
from src.exceptions.exceptions import DeribitClientError


logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Данные о цене криптовалюты."""
    ticker: str
    price: float
    timestamp: int


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

    Использует aiohttp для асинхронных HTTP-запросов.
    Получает index price для указанных валют.

    Attributes:
        session: Асинхронная сессия HTTP. Создаётся при необходимости.
    """

    def __init__(
        self,
        settings_obj=None,
        session: aiohttp.ClientSession | None = None
    ) -> None:
        """
        Инициализация клиента Deribit.

        Args:
            settings_obj: Объект настроек. По умолчанию используется глобальный.
            session: Существующая сессия aiohttp. Если None, создаётся новая.
        """
        self._settings = settings_obj or settings.deribit
        self._session = session

    @property
    def api_url(self) -> str:
        """Получить базовый URL API."""
        return self._settings.API_URL

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Убедиться, что сессия существует."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Закрыть сессию, если она была создана."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _fetch_price(self, ticker: str) -> PriceData:
        """
        Получить цену для одного тикера с Deribit API.

        Args:
            ticker: Тикер валюты (btc_usd или eth_usd)

        Returns:
            PriceData: Данные о цене

        Raises:
            DeribitClientError: При ошибке запроса к API
        """
        # Маппинг тикера к валюте Deribit
        currency_map = {
            "btc_usd": "BTC",
            "eth_usd": "ETH"
        }
        currency = currency_map.get(ticker.lower())

        if not currency:
            raise DeribitClientError(f"Unknown ticker: {ticker}")

        # Deribit API endpoint для получения индекса цены
        url = f"{self.api_url}/public/get_index_price"
        params = {"currency": currency}

        try:
            session = await self._ensure_session()

            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Deribit API error for {ticker}: "
                        f"status={response.status}, body={error_text}"
                    )
                    raise DeribitClientError(
                        f"API returned status {response.status}"
                    )

                data = await response.json()

                # Проверка структуры ответа
                if "result" not in data:
                    raise DeribitClientError(
                        f"Invalid API response structure: {data}"
                    )

                result = data["result"]
                index_price = result.get("index_price")

                if index_price is None:
                    raise DeribitClientError(
                        f"Missing index_price in response: {result}"
                    )

                # Получаем timestamp из API или текущее время
                timestamp = result.get("timestamp", 0) // 1000  # ms to seconds

                return PriceData(
                    ticker=ticker.lower(),
                    price=float(index_price),
                    timestamp=int(timestamp)
                )

        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching {ticker}: {e}")
            raise DeribitClientError(f"Network error: {e}")

    async def fetch_price(self, ticker: str) -> PriceData:
        """
        Получить цену для тикера.

        Alias для _fetch_price для совместимости с интерфейсом.

        Args:
            ticker: Тикер валюты

        Returns:
            PriceData: Данные о цене
        """
        return await self._fetch_price(ticker)

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """
        Получить цены для всех отслеживаемых валют.

        Returns:
            Dict[str, PriceData]: Словарь тикер -> данные о цене
        """
        tickers = ["btc_usd", "eth_usd"]
        prices = {}

        for ticker in tickers:
            try:
                price_data = await self._fetch_price(ticker)
                prices[ticker] = price_data
                logger.info(f"Fetched price for {ticker}: {price_data.price}")
            except DeribitClientError as e:
                logger.error(f"Failed to fetch {ticker}: {e}")
                # Продолжаем с другими тикерами даже при ошибке одного

        return prices

    async def __aenter__(self) -> "DeribitClient":
        """Контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        await self.close()
