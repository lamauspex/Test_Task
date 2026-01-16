""" Клиент API Deribit с использованием aiohttp для асинхронных HTTP-запросов.

Получает индексные цены для BTC/USD и ETH/USD.
"""
from typing import Dict, NamedTuple


class PriceData(NamedTuple):
    """Заглушка для данных о цене."""
    ticker: str
    price: float
    timestamp: int


class DeribitClient:
    """Заглушка для Deribit клиента."""

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """Заглушка для получения всех цен."""
        return {
            "btc_usd": PriceData("btc_usd", 45000.0, 1640995200),
            "eth_usd": PriceData("eth_usd", 3000.0, 1640995200)
        }
