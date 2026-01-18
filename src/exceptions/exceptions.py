"""
Кастомные исключения
"""


class PriceNotFoundError(Exception):
    """Ошибка отсутствия данных о цене"""

    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Нет данных о цене для {self.ticker}: {ticker}")


class DeribitClientError(Exception):
    """Ошибка клиента Deribit API"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Deribit API error: {message}")
