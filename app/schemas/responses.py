"""Все схемы ответов API."""

from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from .base import ticker_field


class PriceRecordResponse(BaseModel):
    """
    Схема ответа для записи о цене.
    Представляет одну запись о цене, возвращаемую API.
    """

    id: int
    ticker: str = ticker_field
    price: Decimal = Field(
        ...,
        description="Цена на момент получения"
    )
    timestamp: int = Field(
        ...,
        description="UNIX timestamp"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp вставки в базу данных"
    )

    class Config:
        from_attributes = True


class PriceLatestResponse(BaseModel):
    """
    Схема ответа для последней цены.
    Возвращает самую последнюю цену для тикера.
    """
    ticker: str = ticker_field
    price: Decimal = Field(
        ...,
        description="Текущая/последняя цена"
    )
    timestamp: int = Field(
        ...,
        description="UNIX timestamp цены"
    )
    fetched_at: datetime = Field(
        ...,
        description="Когда эти данные были получены"
    )


class PriceDateRangeResponse(BaseModel):
    """
    Схема ответа для истории цен с фильтром по диапазону дат.
    Возвращает все цены в указанном диапазоне времени.
    """
    ticker: str = ticker_field
    start_date: int = Field(
        ...,
        description="Начальный UNIX timestamp"
    )
    end_date: int = Field(
        ...,
        description="Конечный UNIX timestamp"
    )
    count: int = Field(
        ...,
        description="Количество возвращённых записей"
    )
    prices: List[PriceRecordResponse] = Field(
        ...,
        description="Список записей о ценах"
    )


class ErrorResponse(BaseModel):
    """Схема для ответов об ошибках."""
    detail: str
