"""Параметры запросов."""

from pydantic import Field

from .base import (
    TickerBase,
    TickerWithPaginationRequest,
    DateRangeRequest
)


class DateRangeQueryParams(TickerBase):
    """Параметры запроса с фильтром по диапазону дат."""

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


class AllPricesQuery(TickerWithPaginationRequest):
    """Запрос всех цен по тикеру."""
    pass


class LatestPriceQuery(TickerBase):
    """Запрос последней цены."""
    pass


class DateRangePricesQuery(DateRangeRequest):
    """Запрос цен по диапазону дат."""
    pass
