"""Все схемы ответов API."""

from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from .base import TickerField


class PriceRecordResponse(BaseModel):
    """
    Схема ответа для записи о цене.
    Представляет одну запись о цене, возвращаемую API.
    """

    ticker: str = TickerField
    price: Decimal = Field(
        ...,
        description="Цена валюты"
    )
    timestamp: int = Field(
        ...,
        ge=0,
        description="Время в UNIX timestamp"
    )
    created_at: datetime = Field(
        ...,
        description="Время создания записи в БД"
    )


class PriceLatestResponse(BaseModel):
    """
    Схема ответа для последней цены.
    Возвращает самую свежую запись о цене для валюты.
    """

    ticker: str = TickerField
    price: Decimal = Field(
        ...,
        description="Последняя цена валюты"
    )
    timestamp: int = Field(
        ...,
        ge=0,
        description="Время в UNIX timestamp"
    )
    fetched_at: datetime = Field(
        ...,
        description="Время получения цены"
    )


class PriceDateRangeResponse(BaseModel):
    """
    Схема ответа для цен по диапазону дат.
    Возвращает список записей о ценах в указанном диапазоне.
    """

    ticker: str = TickerField
    start_date: int = Field(
        ...,
        ge=0,
        description="Начальная дата диапазона (UNIX timestamp)"
    )
    end_date: int = Field(
        ...,
        ge=0,
        description="Конечная дата диапазона (UNIX timestamp)"
    )
    count: int = Field(
        ...,
        ge=0,
        description="Количество возвращённых записей"
    )
    prices: List[PriceRecordResponse] = Field(
        default_factory=list,
        description="Список записей о ценах"
    )


class ErrorResponse(BaseModel):
    """
    Схема ответа для ошибок.
    Стандартная схема для всех HTTP ошибок.
    """

    detail: str = Field(
        ...,
        description="Описание ошибки"
    )
