"""Параметры запросов."""

from pydantic import Field

from .base import (
    DateRangeBase,
    PaginationBase,
    TickerBase
)


class DateRangePricesQuery(TickerBase, DateRangeBase):
    """ Запрос цен по диапазону дат """
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Максимальное количество записей"
    )


class AllPricesQuery(TickerBase, PaginationBase):
    """ Запрос всех цен по тикеру """
    pass


class LatestPriceQuery(TickerBase):
    """ Запрос последней цены """
    pass
