"""API маршруты для эндпоинтов данных о ценах.

Реализует обязательные GET методы с параметром тикера.
Вся валидация осуществляется через Pydantic схемы.
"""
from contextlib import asynccontextmanager
from typing import List, AsyncGenerator

from fastapi import (
    APIRouter,
    Depends,
)

from src.database import get_db
from src.database.database import DatabaseManager
from src.database.uow import UnitOfWork
from src.schemas.responses import (
    PriceRecordResponse,
    PriceLatestResponse,
    PriceDateRangeResponse
)
from src.schemas.requests import (
    AllPricesQuery,
    LatestPriceQuery,
    DateRangePricesQuery
)
from src.services.price_service import PriceService


router = APIRouter(
    prefix="/v1/prices",
    tags=["Цены"]
)


@asynccontextmanager
async def get_uow(
    db: DatabaseManager = Depends(get_db),
) -> AsyncGenerator[UnitOfWork, None]:
    """
    Получить UnitOfWork для использования в эндпоинтах.

    FastAPI управляет созданием и закрытием контекста.
    При ошибке — автоматический rollback.
    При успехе — автоматический commit.

    Args:
        db: Менеджер базы данных (DI)

    Yields:
        UnitOfWork: Готовый к использованию UnitOfWork
    """
    async with UnitOfWork(db) as uow:
        yield uow


@router.get(
    "/all",
    response_model=List[PriceRecordResponse],
    summary="Получить все цены по тикеру",
    description="Возвращает все сохранённые записи о ценах"
)
async def get_all_prices(
    query: AllPricesQuery = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    service: PriceService = Depends(PriceService),
) -> List[PriceRecordResponse]:
    """
    Получить все записи о ценах для указанного тикера.

    Args:
        query: Параметры запроса с валидацией
        uow: Unit of Work (автоматически создаётся и закрывается)
        service: Сервис цен (DI)

    Returns:
        List[PriceRecordResponse]: Список записей о ценах
    """
    return await service.get_prices_by_ticker(
        uow=uow,
        ticker=query.ticker,
        limit=query.limit,
        offset=query.offset
    )


@router.get(
    "/latest",
    response_model=PriceLatestResponse,
    summary="Получить последнюю цену по тикеру",
    description="Возвращает последную запись о цене "
)
async def get_latest_price(
    query: LatestPriceQuery = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    service: PriceService = Depends(PriceService),
) -> PriceLatestResponse:
    """
    Получить последнюю цену для указанного тикера.

    Args:
        query: Параметры запроса с валидацией
        uow: Unit of Work
        service: Сервис цен (DI)

    Returns:
        PriceLatestResponse: Последняя запись о цене
    """
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
    summary="Получить цены по диапазону дат",
    description="Возвращает записи о цене в указанном диапазоне "
)
async def get_prices_by_date_range(
    query: DateRangePricesQuery = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    service: PriceService = Depends(PriceService),
) -> PriceDateRangeResponse:
    """
    Получить записи о ценах для тикера в диапазоне дат.

    Args:
        query: Параметры запроса с валидацией
        uow: Unit of Work
        service: Сервис цен (DI)

    Returns:
        PriceDateRangeResponse: Список записей о ценах в диапазоне дат
    """
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
        prices=prices
    )
