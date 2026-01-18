"""Маппинг тикеров Deribit."""

from typing import Dict


class DeribitMapper:
    """Маппинг тикеров для API Deribit."""

    # Маппинг тикера к валюте Deribit
    TICKER_TO_CURRENCY: Dict[str, str] = {
        "btc_usd": "BTC",
        "eth_usd": "ETH",
    }

    def get_currency(self, ticker: str) -> str | None:
        """Получить валюту для тикера."""
        return self.TICKER_TO_CURRENCY.get(ticker.lower())

    def is_valid_ticker(self, ticker: str) -> bool:
        """Проверить, является ли тикер валидным."""
        return ticker.lower() in self.TICKER_TO_CURRENCY


# Экземпляр для удобного использования
deribit_mapper = DeribitMapper()
