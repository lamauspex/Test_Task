"""Периодические задачи Celery для получения цен криптовалют"""

import asyncio
import logging

from celery.exceptions import SoftTimeLimitExceeded
from celery_app import celery_app
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from config import settings
from database import UnitOfWork
from services import PriceService

logger = logging.getLogger(__name__)


def get_engine():
    """Создать новый движок БД для текущего event loop."""
    return create_async_engine(settings.data_config.get_database_url())


async def _fetch_prices_async() -> dict:
    """
    Асинхронная функция для получения и сохранения цен.

    Единая транзакция для всей операции (Unit of Work).
    """
    service = PriceService()

    # Создаём новый engine и session_factory для текущего loop
    engine = get_engine()
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    try:
        async with async_session() as session:
            async with UnitOfWork(session) as uow:
                saved_tickers = await service.fetch_and_save_all_prices(uow)

        logger.info(
            f"Successfully fetched and saved prices for: {saved_tickers}")
        return {
            "status": "success",
            "count": len(saved_tickers),
            "tickers": saved_tickers
        }
    finally:
        # Закрываем engine после использования
        await engine.dispose()


@celery_app.task(
    bind=True,
    soft_time_limit=settings.celery_config.FETCH_SOFT_TIME_LIMIT
)
def fetch_crypto_prices(self):
    """
    Получить текущие цены криптовалют с Deribit и сохранить в БД.

    Задача запускается Celery Beat каждую минуту.
    Использует soft_time_limit для graceful shutdown.
    """
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Fetching prices..."}
        )
        logger.info("Starting crypto price fetch task")

        # Запускаем асинхронный код в новом event loop
        result = asyncio.run(_fetch_prices_async())
        return result

    except SoftTimeLimitExceeded:
        logger.warning("Task fetch_crypto_prices timed out")
        return {
            "status": "timeout",
            "message": "Task exceeded soft time limit"
        }
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        raise self.retry(
            exc=e,
            countdown=settings.celery_config.FETCH_RETRY_COUNTDOWN,
            max_retries=settings.celery_config.FETCH_MAX_RETRIES
        )
