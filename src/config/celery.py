""" Конфигурация Celery """

from pydantic import Field

from src.config.base import BaseConfig
from src.config.redis import redis_config


class CeleryConfig(BaseConfig):
    """ Конфигурация Celery """

    FETCH_INTERVAL: int = Field(
        default=60,
        description="Интервал получения цен в секундах"
    )

    @property
    def broker_url(self) -> str:
        """Получить URL брокера для Redis."""
        return redis_config.url

    @property
    def result_backend(self) -> str:
        """Получить URL бэкенда результатов для Redis."""
        return f"redis://{redis_config.HOST}:{redis_config.PORT}/{redis_config.DB + 1}"


celery_config = CeleryConfig()
