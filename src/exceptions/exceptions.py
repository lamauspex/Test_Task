"""
Кастомные исключения
"""


class PriceNotFoundError(Exception):
    """Ошибка отсутствия данных о цене"""

    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Нет данных о цене для {self.ticker}: {ticker}")
