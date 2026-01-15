"""Параметры запросов."""


from pydantic import Field

from .base import (
    TickerBase,
    TickerWithPaginationRequest,
    DateRangeRequest
)


class DateRangeQueryParams(TickerBase):
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


"""Схемы для запросов API с валидацией."""


class AllPricesQuery(TickerWithPaginationRequest):
    """Схема запроса для получения всех цен по тикеру."""
    pass


class LatestPriceQuery(TickerBase):
    """Схема запроса для получения последней цены."""
    pass


class DateRangePricesQuery(DateRangeRequest):
    """Схема запроса для получения цен по диапазону дат."""
    pass
