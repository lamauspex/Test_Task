
from typing import Annotated

from pydantic import AfterValidator

from app.config import get_settings, TickerEnum


class TickerValidator:
    """Валидатор тикера криптовалюты."""

    def __call__(self, value: str) -> str:
        settings = get_settings()
        valid = settings.valid_tickers

        ticker = value.lower().strip()
        if ticker not in valid:
            raise ValueError(
                f"Неверный тикер. Допустимые: {', '.join(valid)}"
            )
        return ticker


TickerStr = Annotated[str, AfterValidator(TickerValidator())]


# Для типизации
TickerEnumType = TickerEnum
