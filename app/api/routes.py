"""API маршруты для эндпоинтов данных о ценах.

Реализует обязательные GET методы с параметром тикера.
Вся валидация осуществляется через Pydantic схемы.
"""
from typing import List

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.responses import (
    PriceRecordResponse,
    PriceLatestResponse,
    PriceDateRangeResponse
)
from app.schemas.requests import (
    AllPricesQuery,
    LatestPriceQuery,
    DateRangePricesQuery
)
from app.services.price_service import PriceService, get_price_service


router = APIRouter(
    prefix="/api/v1/prices",
    tags=["Цены"]
)


@router.get(
    "",
    response_model=List[PriceRecordResponse],
    summary="Получить все цены по тикеру",
    description="Возвращает все сохранённые записи о ценах для указанной криптовалюты."
)
async def get_all_prices(
    query: AllPricesQuery = Depends(),
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
) -> List[PriceRecordResponse]:
    """
    Получить все записи о ценах для указанного тикера.

    Args:
        query: Параметры запроса с валидацией
        service: Сервис цен (DI)
        db: Сессия базы данных (DI)

    Returns:
        List[PriceRecordResponse]: Список записей о ценах
    """
    prices = await service.get_prices_by_ticker(
        ticker=query.ticker,
        limit=query.limit,
        offset=query.offset
    )

    return prices


@router.get(
    "/latest",
    response_model=PriceLatestResponse,
    summary="Получить последнюю цену по тикеру",
    description="Возвращает самую свежую запись о цене для указанной криптовалюты."
)
async def get_latest_price(
    query: LatestPriceQuery = Depends(),
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
) -> PriceLatestResponse:
    """
    Получить последнюю цену для указанного тикера.

    Args:
        query: Параметры запроса с валидацией
        service: Сервис цен (DI)
        db: Сессия базы данных (DI)

    Returns:
        PriceLatestResponse: Последняя запись о цене
    """
    record = await service.get_latest_price(query.ticker)
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
    description="Возвращает записи о ценах для тикера в указанном диапазоне UNIX timestamp."
)
async def get_prices_by_date_range(
    query: DateRangePricesQuery = Depends(),
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
) -> PriceDateRangeResponse:
    """
    Получить записи о ценах для тикера в диапазоне дат.

    Args:
        query: Параметры запроса с валидацией
        service: Сервис цен (DI)
        db: Сессия базы данных (DI)

    Returns:
        PriceDateRangeResponse: Список записей о ценах в диапазоне дат
    """
    prices = await service.get_prices_by_date_range(
        ticker=query.ticker,
        start_date=query.start_date,
        end_date=query.end_date,
        limit=query.limit
    )

    return PriceDateRangeResponse(
        ticker=query.ticker,
        start_date=query.start_date,
        end_date=query.end_date,
        count=len(prices),
        prices=prices
    )
