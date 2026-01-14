"""Базовые классы, утилиты и переиспользуемые валидаторы."""


from pydantic import BaseModel, Field

from app.types import TickerStr


class TickerQueryParams(BaseModel):
    """
    Общие параметры запроса для эндпоинтов с тикером
    Валидирует параметр тикера
    """

    # Общие Field-ы для переиспользования
    ticker_field = Field(
        ...,
        min_length=1,
        description="Пара криптовалют (btc_usd или eth_usd)"
    )

    timestamp_field = Field(
        ...,
        ge=0,
        description="UNIX timestamp"
    )

    price_field = Field(
        ...,
        description="Цена"
    )

    ticker: TickerStr
