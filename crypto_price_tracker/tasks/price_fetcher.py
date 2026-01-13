"""
Задачи Celery для периодического получения цен
Содержит задачу для регулярного получения цен с Deribit API
"""
import logging

from tasks.celery import celery_app
from app.services.price_service import price_service

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.price_fetcher.fetch_all_prices",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def fetch_all_prices(self) -> dict:
    """
    Получить все цены с Deribit и сохранить в базу данных

    Периодическая задача, вызываемая Celery beat.
    Повторяет попытку до 3 раз при неудаче.

    Returns:
        dict: Результат операции с количеством сохранённых записей
    """
    try:
        logger.info("Задача получения цен запущена")

        # Синхронный вызов асинхронного сервиса
        import asyncio

        async def _fetch():
            return await price_service.fetch_and_save_all_prices()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            records = loop.run_until_complete(_fetch())
        finally:
            loop.close()

        result = {
            "status": "success",
            "records_saved": len(records),
            "tickers": [r.ticker for r in records]
        }

        logger.info(
            f"Задача выполнена успешно: сохранено {len(records)} записей")

        return result

    except Exception as exc:
        logger.error(f"Ошибка при получении цен: {exc}")

        # Повторная попытка с экспоненциальной задержкой
        retry_delay = self.default_retry_delay * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_delay)


def setup_periodic_tasks(celery_app) -> None:
    """
    Настроить периодические задачи Celery

    Args:
        celery_app: Экземпляр приложения Celery
    """
    from app.config import get_settings

    settings = get_settings()

    # Добавление задачи в расписание, если ещё не добавлена
    celery_app.conf.beat_schedule.setdefault(
        "fetch-prices-every-minute",
        {
            "task": "tasks.price_fetcher.fetch_all_prices",
            "schedule": settings.fetch_interval,
        },
    )
