
from fastapi import HTTPException


def validate_ticker(ticker: str) -> str:
    """
    Валидировать тикер криптовалюты.

    Args:
        ticker: Пара криптовалют

    Returns:
        str: Валидированный тикер в нижнем регистре

    Raises:
        HTTPException: Если тикер неверный
    """
    ticker = ticker.lower().strip()
    if ticker not in ("btc_usd", "eth_usd"):
        raise HTTPException(
            status_code=400,
            detail="Неверный тикер. Должен быть 'btc_usd' или 'eth_usd'"
        )
    return ticker
