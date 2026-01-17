"""
Кастомные исключения
"""


class PriceNotFoundError(Exception):
    """Ошибка отсутствия данных о цене"""

    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Price data not found for ticker: {ticker}")
