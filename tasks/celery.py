"""
Конфигурация Celery для периодических задач.

Настраивает Celery с Redis в качестве брокера.
"""
from celery import Celery

from app.config import get_settings


def create_celery_app() -> Celery:
    """
    Фабрика для создания экземпляра Celery.

    Returns:
        Celery: Настроенный экземпляр Celery
    """
    settings = get_settings()

    celery_app = Celery(
        "crypto_price_tracker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["tasks.price_fetcher"]
    )

    # Конфигурация Celery
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        beat_schedule={
            "fetch-prices-every-minute": {
                "task": "tasks.price_fetcher.fetch_all_prices",
                "schedule": settings.fetch_interval,  # 60 секунд по умолчанию
            },
        },
        task_routes={
            "tasks.price_fetcher.*": {"queue": "default"},
        },
    )

    return celery_app


# Создание экземпляра Celery
celery_app = create_celery_app()
