""" Конфигурация Celery """

from pydantic import Field
from celery import Celery

from src.config.base import BaseConfig


class CeleryConfig(BaseConfig):
    """ Конфигурация Celery """

    FETCH_INTERVAL: int = Field(
        description="Интервал получения цен в секундах")

    # Redis настройки
    REDIS_HOST: str = Field(description="Redis хост")
    REDIS_PORT: int = Field(description="Redis порт")
    REDIS_DB: int = Field(description="Redis база данных")

    @property
    def broker_url(self) -> str:
        """Получить URL брокера для Redis."""

        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def result_backend(self) -> str:
        """Получить URL бэкенда результатов для Redis."""

        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB + 1}"


celery_config = CeleryConfig()

# Инициализация Celery с Redis как брокером
celery_app = Celery(
    __name__,
    broker=celery_config.broker_url,
    backend=celery_config.result_backend,
    include=["src.tasks.price_fetcher"]
)

# Конфигурация Celery
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
            "task": "src.tasks.price_fetcher.fetch_crypto_prices",
            "schedule": celery_config.FETCH_INTERVAL,  # в секундах
            # истекает за 50 сек чтобы не накладывались
            "options": {"expires": 50}
        },
    },
)
