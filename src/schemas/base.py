"""Базовые схемы с валидацией."""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from src.utils.types import VALID_TICKERS


TickerField = Field(
    ...,
    min_length=1,
    description="Пара криптовалют (btc_usd или eth_usd)",
    examples=["btc_usd"]
)


class BaseSchema(BaseModel):
    """Базовый класс для всех схем."""

    model_config = {"from_attributes": True}


class TickerBase(BaseSchema):
    """Базовая схема с тикером."""

    ticker: Annotated[str, TickerField]

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Валидация тикера криптовалюты."""
        ticker_clean = v.lower().strip()
        if ticker_clean not in VALID_TICKERS:
            raise ValueError(
                f"Неверный тикер. Допустимые: {', '.join(VALID_TICKERS)}"
            )
        return ticker_clean


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
    ticker: Annotated[str, TickerField]


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
