"""
API маршруты для эндпоинтов данных о ценах
Реализует обязательные GET методы с параметром тикера
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    ErrorResponse,
    PriceRecordResponse
)
from app.services.price_service import price_service

router = APIRouter(prefix="/api/v1/prices", tags=["Цены"])


@router.get(
    "",
    response_model=List[PriceRecordResponse],
    responses={400: {"model": ErrorResponse}},
    summary="Получить все цены по тикеру",
    description="Возвращает все сохранённые записи о ценах"
)
async def get_all_prices(
    ticker: str = Query(
        ...,
        description="Пара криптовалют (btc_usd или eth_usd)",
        examples=["btc_usd"]
    ),
    db: AsyncSession = Depends(get_db)
) -> List[PriceRecordResponse]:
    """
    Получить все записи о ценах для указанного тикера

    Возвращает список всех сохранённых записей о ценах для тикера,
    упорядоченных по timestamp в порядке убывания

    Args:
        ticker: Пара криптовалют (btc_usd или eth_usd)
        db: Сессия базы данных

    Returns:
        List: Список записей о ценах

    Raises:
        HTTPException 400: Если тикер неверный
    """
    # Валидация тикера
    ticker = ticker.lower().strip()
    if ticker not in ("btc_usd", "eth_usd"):
        raise HTTPException(
            status_code=400,
            detail="Неверный тикер. Должен быть 'btc_usd' или 'eth_usd'"
        )

    prices = await price_service.get_prices_by_ticker(ticker)

    return prices


@router.get(
    "/latest",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Получить последнюю цену по тикеру",
    description="Возвращает самую свежую запись о цене"
)
async def get_latest_price(
    ticker: str = Query(
        ...,
        description="Пара криптовалют (btc_usd или eth_usd)",
        examples=["btc_usd"]
    ),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Получить последнюю цену для указанного тикера
    Возвращает самую недавнюю сохранённую запись о цене для тикера

    Args:
        ticker: Пара криптовалют (btc_usd или eth_usd)
        db: Сессия базы данных

    Returns:
        dict: Последняя запись о цене

    Raises:
        HTTPException 400: Если тикер неверный
        HTTPException 404: Если записи о ценах не найдены для тикера
    """
    # Валидация тикера
    ticker = ticker.lower().strip()
    if ticker not in ("btc_usd", "eth_usd"):
        raise HTTPException(
            status_code=400,
            detail="Неверный тикер. Должен быть 'btc_usd' или 'eth_usd'"
        )

    record = await price_service.get_latest_price(ticker)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Записи о ценах не найдены для тикера: {ticker}"
        )

    return {
        "ticker": record.ticker,
        "price": str(record.price),
        "timestamp": record.timestamp,
        "fetched_at": record.created_at.isoformat()
    }


@router.get(
    "/date-range",
    response_model=List[PriceRecordResponse],
    responses={400: {"model": ErrorResponse}},
    summary="Получить цены по диапазону дат",
    description="Возвращает записи о ценах для тикера в указанном диапазоне UNIX timestamp."
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
    db: AsyncSession = Depends(get_db)
) -> List[PriceRecordResponse]:
    """
    Получить записи о ценах для тикера в диапазоне дат.

    Возвращает все записи о ценах для тикера между указанными
    UNIX timestamp, упорядоченные по timestamp в порядке убывания.

    Args:
        ticker: Пара криптовалют (btc_usd или eth_usd)
        start_date: Начало диапазона дат (UNIX timestamp)
        end_date: Конец диапазона дат (UNIX timestamp)
        db: Сессия базы данных

    Returns:
        List: Список записей о ценах в диапазоне дат

    Raises:
        HTTPException 400: Если параметры неверные
    """
    # Валидация тикера
    ticker = ticker.lower().strip()
    if ticker not in ("btc_usd", "eth_usd"):
        raise HTTPException(
            status_code=400,
            detail="Неверный тикер. Должен быть 'btc_usd' или 'eth_usd'"
        )

    # Валидация диапазона дат
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date должен быть больше или равен start_date"
        )

    async with get_db() as session:
        from sqlalchemy import select, and_
        from app.models import PriceRecord
        from app.schemas import PriceRecordResponse

        query = (
            select(PriceRecord)
            .where(
                and_(
                    PriceRecord.ticker == ticker,
                    PriceRecord.timestamp >= start_date,
                    PriceRecord.timestamp <= end_date
                )
            )
            .order_by(PriceRecord.timestamp.desc())
        )

        result = await session.execute(query)
        records = result.scalars().all()

        return [PriceRecordResponse.model_validate(r) for r in records]


@router.get(
    "/health",
    tags=["Здоровье"],
    summary="Проверка здоровья",
    description="Простой эндпоинт для проверки работоспособности."
)
async def health_check() -> dict:
    """
    Эндпоинт проверки здоровья.

    Returns:
        dict: Статус работоспособности
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
