"""
Схемы Pydantic для валидации запросов и ответов.

Предоставляет валидацию данных и сериализацию для API операций.
"""
from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, field_validator


class PriceRecordResponse(BaseModel):
    """
    Схема ответа для записи о цене.

    Представляет одну запись о цене, возвращаемую API.
    """
    id: int
    ticker: str = Field(..., description="Пара криптовалют (btc_usd, eth_usd)")
    price: Decimal = Field(..., description="Цена на момент получения")
    timestamp: int = Field(..., description="UNIX timestamp")
    created_at: datetime = Field(...,
                                 description="Timestamp вставки в базу данных")

    class Config:
        from_attributes = True


class PriceLatestResponse(BaseModel):
    """
    Схема ответа для последней цены.

    Возвращает самую последнюю цену для тикера.
    """
    ticker: str = Field(..., description="Пара криптовалют")
    price: Decimal = Field(..., description="Текущая/последняя цена")
    timestamp: int = Field(..., description="UNIX timestamp цены")
    fetched_at: datetime = Field(...,
                                 description="Когда эти данные были получены")


class PriceDateRangeResponse(BaseModel):
    """
    Схема ответа для истории цен с фильтром по диапазону дат.

    Возвращает все цены в указанном диапазоне времени.
    """
    ticker: str = Field(..., description="Пара криптовалют")
    start_date: int = Field(..., description="Начальный UNIX timestamp")
    end_date: int = Field(..., description="Конечный UNIX timestamp")
    count: int = Field(..., description="Количество возвращённых записей")
    prices: List[PriceRecordResponse] = Field(
        ..., description="Список записей о ценах")


class ErrorResponse(BaseModel):
    """Схема для ответов об ошибках."""
    detail: str


class TickerQueryParams(BaseModel):
    """
    Общие параметры запроса для эндпоинтов с тикером.

    Валидирует параметр тикера.
    """
    ticker: str = Field(
        ...,
        description="Пара криптовалют (btc_usd или eth_usd)",
        min_length=1,
    )

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Валидация формата тикера."""
        ticker = v.lower().strip()
        valid_tickers = ("btc_usd", "eth_usd")
        if ticker not in valid_tickers:
            raise ValueError(
                f"Неверный тикер. Должен быть один из: {valid_tickers}")
        return ticker


class DateRangeQueryParams(TickerQueryParams):
    """
    Параметры запроса с фильтром по диапазону дат.

    Расширяет валидацию тикера параметрами диапазона дат.
    """
    start_date: int = Field(
        ...,
        ge=0,
        description="Начальная дата как UNIX timestamp"
    )
    end_date: int = Field(
        ...,
        ge=0,
        description="Конечная дата как UNIX timestamp"
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: int, info) -> int:
        """Убедиться, что end_date больше или равен start_date."""
        start = info.data.get("start_date", 0)
        if v < start:
            raise ValueError(
                "end_date должен быть больше или равен start_date")
        return v
