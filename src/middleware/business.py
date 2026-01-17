"""
Lогирование бизнес-логики приложения
"""

import logging
from datetime import datetime


class BusinessLogicLogger:
    """Централизованное логирование бизнес-логики приложения."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)

    def log_price_saved(
        self,
        ticker: str,
        price: float,
        timestamp: int
    ) -> None:
        """Логирование сохранения цены."""

        self.logger.debug(
            f"Сохранена запись о цене: {ticker} = {price} "
            f"@ {datetime.fromtimestamp(timestamp)}"
        )

    def log_prices_saved(self, tickers: list[str]) -> None:
        """Логирование сохранения множественных цен."""
        self.logger.info(
            f"Сохранены цены для тикеров: {', '.join(tickers)}"
        )


# Глобальный инстанс логгера бизнес-логики
_business_logger: BusinessLogicLogger | None = None


def get_business_logger() -> BusinessLogicLogger:
    """
    Получить инстанс бизнес-логгера.

    Returns:
        BusinessLogicLogger: Инстанс логгера
    """
    global _business_logger
    if _business_logger is None:
        _business_logger = BusinessLogicLogger()
    return _business_logger
