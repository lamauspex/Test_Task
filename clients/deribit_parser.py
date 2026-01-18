"""Парсинг ответа API Deribit."""

from dataclasses import dataclass

from src.exceptions.exceptions import DeribitClientError


@dataclass
class PriceData:
    """Данные о цене криптовалюты."""
    ticker: str
    price: float
    timestamp: int


class DeribitParser:
    """Парсинг ответа API Deribit."""

    def parse_price_response(self, data: dict, ticker: str) -> PriceData:
        """
        Парсить ответ API для получения цены.

        Args:
            data: Ответ от API
            ticker: Тикер валюты

        Returns:
            PriceData: Данные о цене

        Raises:
            DeribitClientError: При ошибке парсинга
        """
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

        timestamp = result.get("timestamp", 0) // 1000  # ms to seconds

        return PriceData(
            ticker=ticker.lower(),
            price=float(index_price),
            timestamp=int(timestamp)
        )


# Экземпляр для удобного использования
deribit_parser = DeribitParser()
