"""
Клиент API Deribit.

Удобный импорт основных классов:

    from clients import DeribitClient, PriceData, IDeribitClient
"""

from .deribit_client import (
    DeribitClient,
    IDeribitClient,
)

from .deribit_parser import (
    PriceData,
)

from .deribit_http_client import (
    DeribitHttpClient,
)

from .deribit_mapper import (
    DeribitMapper,
    deribit_mapper,
)

__all__ = [
    "DeribitClient",
    "IDeribitClient",
    "PriceData",
    "DeribitHttpClient",
    "DeribitMapper",
    "deribit_mapper",
]
