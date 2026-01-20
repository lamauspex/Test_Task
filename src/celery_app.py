"""
Инициализация Celery приложения
"""

from celery import Celery

from config import settings


# Создание Celery app
celery_app = Celery(
    "crypto_price_tracker",
    broker=settings.celery_config.broker_url,
    backend=settings.celery_config.result_backend,
    include=["tasks.price_fetcher"]
)

# Конфигурация
celery_app.conf.update(
    broker_url=settings.celery_config.broker_url,
    result_backend=settings.celery_config.result_backend,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    task_compression="gzip",
    broker_connection_retry_on_startup=True,

    # Настройка beat (планировщика задач)
    beat_schedule={
        "fetch-crypto-prices-every-minute": {
            "task": "tasks.price_fetcher.fetch_crypto_prices",
            "schedule": settings.celery_config.FETCH_INTERVAL,
            "options": {"expires": 50}
        },
    },
)
