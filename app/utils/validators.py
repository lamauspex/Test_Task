"""Утилиты для валидации данных."""

from typing import Literal
from app.config import get_settings


def validate_ticker(ticker: str) -> Literal["btc_usd", "eth_usd"]:
    """
    Валидация тикера криптовалюты.

    Args:
        ticker: Тикер криптовалюты

    Returns:
        Литерал "btc_usd" или "eth_usd"

    Raises:
        ValueError: Если тикер неверный
    """
    settings = get_settings()
    valid_tickers = settings.valid_tickers

    ticker_clean = ticker.lower().strip()
    if ticker_clean not in valid_tickers:
        raise ValueError(
            f"Неверный тикер. Допустимые: {', '.join(valid_tickers)}")

    return ticker_clean  # type: ignore[return-value]


def validate_date_range(start_date: int, end_date: int) -> None:
    """
    Валидация диапазона дат.

    Args:
        start_date: Начальная дата (UNIX timestamp)
        end_date: Конечная дата (UNIX timestamp)

    Raises:
        ValueError: Если диапазон неверный
    """
    if end_date < start_date:
        raise ValueError("end_date должен быть больше или равен start_date")

    if start_date < 0 or end_date < 0:
        raise ValueError("Даты должны быть положительными числами")
