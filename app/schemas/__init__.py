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
    # Responses
    "PriceRecordResponse",
    "PriceLatestResponse",
    "PriceDateRangeResponse",
    "ErrorResponse",
    # Base
    "BaseSchema",
    "TickerBase",
    "DateRangeBase",
    "PaginationBase",
    "TickerOnlyRequest",
    "TickerWithPaginationRequest",
    "DateRangeRequest",
    # Requests
    "AllPricesQuery",
    "LatestPriceQuery",
    "DateRangePricesQuery"
]
