""" Конфигурация Celery """

from pydantic import Field
from celery import Celery

from src.config.base import BaseConfig
from src.config.database import database_config


class CeleryConfig(BaseConfig):
    """ Конфигурация Celery """

    FETCH_INTERVAL: int = Field(
        default=60,
        description="Интервал получения цен в секундах"
    )


celery_config = CeleryConfig()

# Формируем URL для PostgreSQL брокера
DATABASE_URL = database_config.get_database_url()
BROKER_URL = f"db+{DATABASE_URL}"
RESULT_BACKEND = f"db+{DATABASE_URL}"

# Инициализация Celery
celery_app = Celery(
    __name__,
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.tasks.price_fetcher"]
)

# Конфигурация Celery
celery_app.conf.update(
    broker_url=BROKER_URL,
    result_backend=RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
    task_compression="gzip",
    broker_connection_retry_on_startup=True,
)
