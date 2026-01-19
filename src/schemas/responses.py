"""Схемы ответов API."""

from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from .base import TickerBase


class PriceRecordResponse(TickerBase):
    """Запись о цене."""

    price: Decimal = Field(..., description="Цена валюты")
    timestamp: int = Field(..., ge=0, description="Время в UNIX timestamp")
    created_at: datetime = Field(..., description="Время создания записи в БД")


class PriceLatestResponse(TickerBase):
    """Последняя цена."""

    price: Decimal = Field(..., description="Последняя цена валюты")
    timestamp: int = Field(..., ge=0, description="Время в UNIX timestamp")
    fetched_at: datetime = Field(..., description="Время получения цены")


class PriceDateRangeResponse(TickerBase):
    """Цены по диапазону дат."""

    start_date: int = Field(..., ge=0, description="Начало диапазона")
    end_date: int = Field(..., ge=0, description="Конец диапазона")
    count: int = Field(..., ge=0, description="Количество записей")
    prices: List[PriceRecordResponse] = Field(
        default_factory=list,
        description="Список записей о ценах"
    )


class ErrorResponse(BaseModel):
    """Ответ об ошибке."""

    detail: str = Field(..., description="Описание ошибки")
