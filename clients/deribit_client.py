"""
Минимальный клиент API Deribit для получения цен криптовалют.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlencode

import aiohttp

from src.config.settings import settings
from src.exceptions.exceptions import DeribitClientError
from src.utils.types import VALID_TICKERS

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Данные о цене криптовалюты"""
    ticker: str
    price: float
    timestamp: int


class DeribitClient:
    """
    Минимальный клиент для API Deribit
    """

    def __init__(self) -> None:
        """Инициализация клиента."""
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "DeribitClient":
        """
        Контекстный менеджер - вход.
        Создаёт сессию для текущего event loop.
        """
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход. Закрывает сессию."""
        await self.close()

    async def close(self) -> None:
        """Закрыть сессию."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получить существующую сессию или создать новую.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(
        self,
        endpoint: str,
        params: dict | None = None
    ) -> dict:
        """
        Выполнить запрос к Deribit API v2 REST.

        """
        base_url = settings.deribit.DERIBIT_API_URL
        url = f"{base_url}{endpoint}"

        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"

        session = await self._get_session()

        async with session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                raise DeribitClientError(
                    f"API error: status={response.status}, body={error_text}"
                )

            json_response = await response.json()
            if "error" in json_response:
                error = json_response["error"]
                raise DeribitClientError(
                    f"API error: {error.get('message', error)}"
                )

            return json_response

    async def fetch_price(self, ticker: str) -> PriceData:
        """
        Получить цену для тикера.
        """
        ticker = ticker.upper()

        if ticker not in VALID_TICKERS:
            raise DeribitClientError(f"Unsupported ticker: {ticker}")

        # Преобразуем BTC_USD -> BTC, ETH_USD -> ETH
        currency_map = {"BTC_USD": "BTC", "ETH_USD": "ETH"}
        currency = currency_map[ticker]

        result = await self._request(
            endpoint="/ticker",
            params={"instrument_name": f"{currency}-PERPETUAL"}
        )

        if "result" in result:
            index_price = result["result"].get("index_price")
            timestamp = result["result"].get("timestamp")
            if index_price is None:
                raise DeribitClientError(f"Missing index_price for {ticker}")
            timestamp = timestamp // 1000
        else:
            raise DeribitClientError(f"Missing index_price for {ticker}")

        return PriceData(
            ticker=ticker,
            price=float(index_price),
            timestamp=int(timestamp)
        )

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """
        Получить цены для всех поддерживаемых валют
        """
        prices = {}

        for ticker in VALID_TICKERS:
            try:
                price_data = await self.fetch_price(ticker)
                prices[ticker] = price_data
                logger.info(f"Fetched {ticker}: {price_data.price}")
            except DeribitClientError as e:
                logger.error(f"Failed to fetch {ticker}: {e}")

        return prices


# Экземпляр по умолчанию
default_client = DeribitClient()
