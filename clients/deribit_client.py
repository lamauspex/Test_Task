"""
Клиент API Deribit.
"""

from __future__ import annotations
import logging

import aiohttp
from dataclasses import dataclass

from src.config.settings import settings
from src.exceptions.exceptions import DeribitClientError

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Данные о цене криптовалюты."""
    ticker: str
    price: float
    timestamp: int


class DeribitClient:
    """
    Клиент для API криптобиржи Deribit.

    Поддерживает тикеры: btc_usd, eth_usd
    """

    # Маппинг тикера к валюте Deribit
    VALID_TICKERS = {"btc_usd", "eth_usd"}

    def __init__(self) -> None:
        """Инициализация клиента Deribit."""
        self._session: aiohttp.ClientSession | None = None
        self._request_id = 0

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Создать или переиспользовать сессию."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
        return self._session

    async def request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None
    ) -> dict:
        """
        Выполнить JSON-RPC запрос к Deribit API.
        """
        url = f"{settings.deribit.DERIBIT_API_URL}{endpoint}"
        self._request_id += 1

        json_body = {
            "jsonrpc": "2.0",
            "method": endpoint,
            "params": params or {},
            "id": self._request_id
        }

        session = await self._ensure_session()

        async with session.post(url, json=json_body) as response:
            if response.status != 200:
                raise DeribitClientError(
                    f"API error: status={response.status}")

            json_response = await response.json()

            if "error" in json_response:
                error = json_response["error"]
                raise DeribitClientError(
                    f"JSON-RPC error: {error.get('message')}"
                )

            return json_response.get("result", {})

    async def fetch_price(self, ticker: str) -> PriceData:
        """
        Получить цену для тикера.

        Args:
            ticker: Тикер валюты (btc_usd, eth_usd)

        Returns:
            PriceData с ценой и временем

        Raises:
            DeribitClientError: При ошибке API или неизвестном тикере
        """
        ticker = ticker.lower()

        if ticker not in self.VALID_TICKERS:
            raise DeribitClientError(f"Unknown ticker: {ticker}")

        result = await self.request(
            method="GET",
            endpoint="/public/get_index_price",
            params={"index_name": ticker}
        )

        index_price = result.get("index_price")
        if index_price is None:
            raise DeribitClientError("Missing index_price in response")

        timestamp = result.get("timestamp", 0) // 1000

        return PriceData(
            ticker=ticker,
            price=float(index_price),
            timestamp=int(timestamp)
        )

    async def fetch_all_prices(self) -> dict[str, PriceData]:
        """Получить цены для всех поддерживаемых валют."""
        prices = {}

        async with self:
            for ticker in self.VALID_TICKERS:
                try:
                    price_data = await self.fetch_price(ticker)
                    prices[ticker] = price_data
                    logger.info(f"Fetched {ticker}: {price_data.price}")
                except DeribitClientError as e:
                    logger.error(f"Failed to fetch {ticker}: {e}")

        return prices

    async def close(self) -> None:
        """Закрыть HTTP-сессию."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "DeribitClient":
        """Контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        await self.close()


# Экземпляр по умолчанию
default_client = DeribitClient()
