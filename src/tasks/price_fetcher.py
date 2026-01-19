"""Периодические задачи Celery для получения цен криптовалют"""

import logging

from celery.exceptions import SoftTimeLimitExceeded

from celery_app import celery_app
from config import settings, celery_config
from database import DatabaseManager, UnitOfWork
from services import PriceService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    soft_time_limit=celery_config.FETCH_SOFT_TIME_LIMIT
)
def fetch_crypto_prices(self):
    """
    Получить текущие цены криптовалют с Deribit и сохранить в БД.

    Задача запускается Celery Beat каждую минуту.
    Использует soft_time_limit для graceful shutdown.

    Единая транзакция для всей операции (Unit of Work).
    """
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Fetching prices..."}
        )
        logger.info("Starting crypto price fetch task")

        # Единый DatabaseManager на задачу
        database_manager = DatabaseManager(
            settings.data_config.get_database_url())
        service = PriceService()

        # Единая транзакция через UoW
        with UnitOfWork(database_manager) as uow:
            saved_tickers = service.fetch_and_save_all_prices(uow)
            uow.commit()

        logger.info(
            f"Successfully fetched and saved prices for: {saved_tickers}")
        return {
            "status": "success",
            "count": len(saved_tickers),
            "tickers": saved_tickers
        }

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
            countdown=celery_config.FETCH_RETRY_COUNTDOWN,
            max_retries=celery_config.FETCH_MAX_RETRIES
        )
