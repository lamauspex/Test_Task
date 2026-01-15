"""Базовые классы, утилиты и переиспользуемые валидаторы."""


from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Базовый класс для всех схем."""


class TickerQuery(BaseModel):
    """Базовые параметры запроса с тикером."""
    ticker: str = Field(
        ...,
        min_length=1,
        description="Пара криптовалют (btc_usd или eth_usd)",
        examples=["btc_usd"]
    )


class DateRangeQuery(BaseModel):
    """Параметры запроса с диапазоном дат."""
    start_date: int = Field(
        ...,
        ge=0,
        description="Начало диапазона дат как UNIX timestamp",
        examples=[1704067200]
    )
    end_date: int = Field(
        ...,
        ge=0,
        description="Конец диапазона дат как UNIX timestamp",
        examples=[1704153600]
    )


class PaginationParams(BaseModel):
    """Параметры пагинации."""
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимальное количество записей"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Количество записей для пропуска"
    )


# Переиспользуемые поля
ticker_field = Field(
    ...,
    min_length=1,
    description="Пара криптовалют (btc_usd или eth_usд)"
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
