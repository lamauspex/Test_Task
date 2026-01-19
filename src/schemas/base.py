"""Базовые схемы с валидацией."""


from pydantic import BaseModel, Field, field_validator

from utils import VALID_TICKERS


class BaseSchema(BaseModel):
    """Базовый класс для всех схем"""

    model_config = {"from_attributes": True}


class TickerBase(BaseSchema):
    """Базовая схема с тикером"""

    ticker: str = Field(
        ...,
        description=f"Тикер валюты: {', '.join(VALID_TICKERS)}"
    )

    @field_validator("ticker")
    def validate_ticker(cls, v):
        """Валидация тикера криптовалюты"""

        v_upper = v.upper()
        if v_upper not in VALID_TICKERS:
            raise ValueError(f"Тикер должен быть: {VALID_TICKERS}")
        return v_upper


class DateRangeBase(BaseSchema):
    """Базовая схема с диапазоном дат."""
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

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: int, info) -> int:
        """Валидация диапазона дат."""
        start_date = info.data.get("start_date", 0)
        if v < start_date:
            raise ValueError(
                "end_date должен быть больше или равен start_date"
            )
        return v


class PaginationBase(BaseSchema):
    """Базовая схема с пагинацией."""
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


class TickerOnlyRequest(BaseSchema):
    """Запрос только с тикером."""
    pass


class TickerWithPaginationRequest(TickerBase, PaginationBase):
    """Запрос с тикером и пагинацией."""
    pass


class DateRangeRequest(TickerBase, DateRangeBase):
    """Запрос с тикером и диапазоном дат."""
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимальное количество записей"
    )
