"""
Клиент API Deribit.
"""

from __future__ import annotations
import logging
from decimal import Decimal

import aiohttp
from dataclasses import dataclass

from src.config.settings import settings
from src.exceptions.exceptions import DeribitClientError
from src.utils.types import VALID_TICKERS

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Данные о цене криптовалюты."""
    ticker: str
    price: Decimal
    timestamp: int


class DeribitClient:
    """
    Клиент для API криптобиржи Deribit.

    Поддерживает тикеры: btc_usd, eth_usd
    """

    def __init__(self) -> None:
        """Инициализация клиента Deribit."""
        self._session: aiohttp.ClientSession | None = None
        self._request_id = 0
        self._access_token: str | None = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Создать или переиспользовать сессию."""
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self._access_token:
                headers["Authorization"] = f"Bearer {self._access_token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def authenticate(self) -> None:
        """
        Аутентификация и получение токена доступа.
        """
        result = await self.request(
            method="POST",
            endpoint="/public/auth",
            params={
                "grant_type": "client_credentials",
                "client_id": settings.deribit.CLIENT_ID,
                "client_secret": settings.deribit.CLIENT_SECRET
            }
        )
        self._access_token = result.get("access_token")
        logger.info("Successfully authenticated with Deribit API")

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
                error_text = await response.text()
                raise DeribitClientError(
                    f"API error: status={response.status}, body={error_text}"
                )

            json_response = await response.json()

            if "error" in json_response:
                error = json_response["error"]
                raise DeribitClientError(
                    f"JSON-RPC error: {error.get('message')} (code: {error.get('code')})"
                )

            return json_response.get("result", {})

    async def fetch_price(self, ticker: str) -> PriceData:
        """
        Получить цену для тикера.
        """
        ticker = ticker.lower()

        # Преобразуем btc_usd -> BTC, eth_usd -> ETH
        currency_map = {"btc_usd": "BTC", "eth_usd": "ETH"}
        currency = currency_map.get(ticker, ticker.upper())

        result = await self.request(
            method="POST",
            endpoint="/public/get_index",
            params={"currency": currency}
        )

        # Deribit возвращает объект с полем 'index_price'
        index_price = result.get("index_price") if isinstance(
            result, dict) else result
        if index_price is None:
            raise DeribitClientError(
                f"Missing index_price in response: {result}")

        timestamp = result.get("timestamp", 0)
        if timestamp > 0:
            timestamp = timestamp // 1000

        return PriceData(
            ticker=ticker,
            price=Decimal(str(index_price)),
            timestamp=int(timestamp)
        )

    async def fetch_all_prices(self) -> dict[str, PriceData]:
        """Получить цены для всех поддерживаемых валют."""
        prices = {}

        async with self:
            # Сначала аутентифицируемся
            await self.authenticate()

            for ticker in VALID_TICKERS:
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
