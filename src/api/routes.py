"""API маршруты для работы с данными о ценах."""

from typing import List

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, UnitOfWork
from schemas import (
    PriceRecordResponse,
    PriceLatestResponse,
    PriceDateRangeResponse,
    AllPricesQuery,
    LatestPriceQuery,
    DateRangePricesQuery
)

from services import PriceService, get_price_service


router = APIRouter(
    prefix="/v1/prices",
    tags=["Цены"]
)


async def get_uow(
    session: AsyncSession = Depends(get_db),
) -> UnitOfWork:
    """
    Получаем UnitOfWork для использования в эндпоинтах.
    Сессия передаётся из get_db, UnitOfWork только оборачивает её.
    """
    return UnitOfWork(session)


@router.get(
    "/all",
    response_model=List[PriceRecordResponse],
    summary="Получить все цены по тикеру BTC_USD или ETH_USD",
    description="Возвращает все сохранённые записи о ценах"
)
async def get_all_prices(
    query: AllPricesQuery = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    service: PriceService = Depends(get_price_service),
) -> List[PriceRecordResponse]:
    """Получить все записи о ценах для указанного тикера."""

    return list(await service.get_prices_by_ticker(
        uow=uow,
        ticker=query.ticker,
        limit=query.limit,
        offset=query.offset
    ))


@router.get(
    "/latest",
    response_model=PriceLatestResponse,
    summary="Получить последнюю цену BTC_USD или ETH_USD",
    description="Возвращает последнюю запись о цене"
)
async def get_latest_price(
    query: LatestPriceQuery = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    service: PriceService = Depends(get_price_service),
) -> PriceLatestResponse:
    """Получить последнюю цену для указанного тикера."""

    record = await service.get_latest_price(uow, query.ticker)
    return PriceLatestResponse(
        ticker=record.ticker,
        price=record.price,
        timestamp=record.timestamp,
        fetched_at=record.created_at
    )


@router.get(
    "/date-range",
    response_model=PriceDateRangeResponse,
    summary="Получить цены BTC_USD или ETH_USD по диапазону дат",
    description="Возвращает записи о цене в указанном диапазоне"
)
async def get_prices_by_date_range(
    query: DateRangePricesQuery = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    service: PriceService = Depends(get_price_service),
) -> PriceDateRangeResponse:
    """Получить записи о ценах для тикера в диапазоне дат."""

    prices = await service.get_prices_by_date_range(
        uow=uow,
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
        prices=list(prices)
    )
