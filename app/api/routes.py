"""
API маршруты для эндпоинтов данных о ценах.

Реализует обязательные GET методы с параметром тикера.
Вся обработка исключений и логирование вынесены в middleware.
"""
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Query
)
from sqlalchemy.ext.asyncio import AsyncSession


from app.database import get_db
from app.schemas.responses import (
    PriceRecordResponse,
    PriceLatestResponse,
    PriceDateRangeResponse
)
from app.services.price_service import (
    PriceService,
    get_price_service
)


router = APIRouter(
    prefix="/api/v1/prices",
    tags=["Цены"]
)


@router.get(
    "",
    response_model=List[PriceRecordResponse],
    summary="Получить все цены по тикеру",
    description="Возвращает все сохранённые записи \
        о ценах для указанной криптовалюты."
)
async def get_all_prices(
    ticker: str = Query(
        ...,
        description="Пара криптовалют (btc_usd или eth_usd)",
        examples=["btc_usd"]
    ),
    limit: int = Query(default=1000, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
) -> List[PriceRecordResponse]:
    """
    Получить все записи о ценах для указанного тикера.

    Args:
        ticker: Пара криптовалют (btc_usd или eth_usd)
        limit: Максимальное количество записей (1-10000)
        offset: Количество записей для пропуска
        service: Сервис цен (DI)
        db: Сессия базы данных (DI)

    Returns:
        List[PriceRecordResponse]: Список записей о ценах
    """
    prices = await service.get_prices_by_ticker(
        ticker=ticker,
        limit=limit,
        offset=offset
    )

    return prices


@router.get(
    "/latest",
    response_model=PriceLatestResponse,
    summary="Получить последнюю цену по тикеру",
    description="Возвращает самую свежую запись \
        о цене для указанной криптовалюты."
)
async def get_latest_price(
    ticker: str = Query(
        ...,
        description="Пара криптовалют (btc_usd или eth_usd)",
        examples=["btc_usd"]
    ),
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
) -> PriceLatestResponse:
    """
    Получить последнюю цену для указанного тикера.

    Args:
        ticker: Пара криптовалют (btc_usd или eth_usd)
        service: Сервис цен (DI)
        db: Сессия базы данных (DI)

    Returns:
        PriceLatestResponse: Последняя запись о цене
    """
    record = await service.get_latest_price(ticker)
    return PriceLatestResponse(
        ticker=record.ticker,
        price=record.price,
        timestamp=record.timestamp,
        fetched_at=record.created_at
    )


@router.get(
    "/date-range",
    response_model=PriceDateRangeResponse,
    summary="Получить цены по диапазону дат",
    description="Возвращает записи о ценах для тикера \
        в указанном диапазоне UNIX timestamp."
)
async def get_prices_by_date_range(
    ticker: str = Query(
        ...,
        description="Пара криптовалют (btc_usd или eth_usd)",
        examples=["btc_usd"]
    ),
    start_date: int = Query(
        ...,
        ge=0,
        description="Начало диапазона дат как UNIX timestamp",
        examples=[1704067200]
    ),
    end_date: int = Query(
        ...,
        ge=0,
        description="Конец диапазона дат как UNIX timestamp",
        examples=[1704153600]
    ),
    limit: int = Query(default=1000, ge=1, le=10000),
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
) -> PriceDateRangeResponse:
    """
    Получить записи о ценах для тикера в диапазоне дат.

    Args:
        ticker: Пара криптовалют (btc_usd или eth_usd)
        start_date: Начало диапазона дат (UNIX timestamp)
        end_date: Конец диапазона дат (UNIX timestamp)
        limit: Максимальное количество записей (1-10000)
        service: Сервис цен (DI)
        db: Сессия базы данных (DI)

    Returns:
        PriceDateRangeResponse: Список записей о ценах в диапазоне дат
    """
    prices = await service.get_prices_by_date_range(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    return PriceDateRangeResponse(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        count=len(prices),
        prices=prices
    )
