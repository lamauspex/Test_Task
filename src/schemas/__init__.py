"""Схемы Pydantic для API."""

from .responses import (
    PriceRecordResponse,
    PriceLatestResponse,
    PriceDateRangeResponse,
    ErrorResponse
)
from .base import (
    BaseSchema,
    TickerBase,
    DateRangeBase,
    PaginationBase,
    TickerOnlyRequest,
    TickerWithPaginationRequest,
    DateRangeRequest
)
from .requests import (
    AllPricesQuery,
    LatestPriceQuery,
    DateRangePricesQuery
)

__all__ = [
    "PriceRecordResponse",
    "PriceLatestResponse",
    "PriceDateRangeResponse",
    "ErrorResponse",
    "BaseSchema",
    "TickerBase",
    "DateRangeBase",
    "PaginationBase",
    "TickerOnlyRequest",
    "TickerWithPaginationRequest",
    "DateRangeRequest",
    "AllPricesQuery",
    "LatestPriceQuery",
    "DateRangePricesQuery"
]
