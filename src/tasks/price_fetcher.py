""" Периодические задачи Celery для получения цен криптовалют """

import asyncio
import logging

from celery.exceptions import SoftTimeLimitExceeded

from src.celery_app import celery_app
from src.services.price_service import PriceService


logger = logging.getLogger(__name__)


def run_async(coro):
    """Запустить асинхронный код в синхронной среде Celery."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, soft_time_limit=55)
def fetch_crypto_prices(self):
    """
    Получить текущие цены криптовалют с Deribit и сохранить в БД.

    Задача запускается Celery Beat каждую минуту.
    Использует soft_time_limit для graceful shutdown.
    """
    try:
        self.update_state(state="PROGRESS", meta={
                          "status": "Fetching prices..."})
        logger.info("Starting crypto price fetch task")

        service = PriceService()
        # Запускаем async метод в sync контексте Celery
        saved_tickers = run_async(service.fetch_and_save_all_prices())

        logger.info(
            f"Successfully fetched and saved prices for: {saved_tickers}")
        return {"status": "success", "count": len(saved_tickers), "tickers": saved_tickers}

    except SoftTimeLimitExceeded:
        logger.warning("Task fetch_crypto_prices timed out")
        return {"status": "timeout", "message": "Task exceeded soft time limit"}
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        # Пробрасываем исключение для Celery retry механизма
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True)
def save_single_price(self, ticker: str, price: float, timestamp: int):
    """
    Сохранить цену одной криптовалюты.

    Используется для сохранения отдельных тикеров
    или как элементарная операция для отслеживания.

    Args:
        ticker: Тикер валюты (btc_usd, eth_usd)
        price: Цена валюты
        timestamp: UNIX timestamp
    """
    try:
        from clients.deribit_client import PriceData

        service = PriceService()
        price_data = PriceData(ticker=ticker, price=price, timestamp=timestamp)
        run_async(service.save_price_data(price_data))

        logger.info(f"Saved price for {ticker}: {price}")
        return {"status": "success", "ticker": ticker, "price": price}

    except Exception as e:
        logger.error(f"Error saving price for {ticker}: {e}")
        raise self.retry(exc=e, countdown=30, max_retries=2)


@celery_app.task(bind=True)
def health_check(self):
    """
    Проверка работоспособности Celery воркера.

    Returns:
        dict: Статус воркера
    """
    return {
        "status": "healthy",
        "worker": self.request.hostname,
        "pid": self.request.pid
    }
