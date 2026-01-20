"""Периодические задачи Celery для получения цен криптовалют"""

import asyncio
import logging

from celery.exceptions import SoftTimeLimitExceeded
from celery_app import celery_app

from config import settings
from database import DatabaseManager, UnitOfWork
from src.services import PriceService

logger = logging.getLogger(__name__)


async def _fetch_prices_async() -> dict:
    """
    Асинхронная функция для получения и сохранения цен.

    Единая транзакция для всей операции (Unit of Work).
    """
    database_manager = DatabaseManager(
        settings.data_config.get_database_url()
    )
    service = PriceService()

    async with UnitOfWork(database_manager) as uow:
        saved_tickers = await service.fetch_and_save_all_prices(uow)

    logger.info(f"Successfully fetched and saved prices for: {saved_tickers}")
    return {
        "status": "success",
        "count": len(saved_tickers),
        "tickers": saved_tickers
    }


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

        # Запускаем асинхронный код
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
