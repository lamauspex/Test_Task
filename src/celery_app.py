"""
Инициализация Celery приложения.

Использование:
    from src.celery_app import celery_app

    celery -A celery_app worker -l info
    celery -A celery_app beat -l info
"""

from celery import Celery

from config import celery_config


# Создание Celery app
celery_app = Celery(
    "crypto_price_tracker",
    broker=celery_config.broker_url,
    backend=celery_config.result_backend,
    include=["tasks.price_fetcher"]
)

# Конфигурация
celery_app.conf.update(
    broker_url=celery_config.broker_url,
    result_backend=celery_config.result_backend,
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
            "schedule": celery_config.FETCH_INTERVAL,
            "options": {"expires": 50}
        },
    },
)
