""" Конфигурация Celery и Redis """

from pydantic import Field

from app.config.base import BaseConfig


class CeleryConfig(BaseConfig):
    """Конфигурация Celery и Redis"""

    BROKER_URL: str = Field(
        description="URL брокера Celery"
    )
    RESULT_BACKEND: str = Field(
        description="URL бэкенда результатов Celery"
    )
    REDIS_URL: str = Field(
        description="URL Redis"
    )


celery_config = CeleryConfig()
