""" Конфигурация Redis """

from pydantic import Field

from .base import BaseConfig


class RedisConfig(BaseConfig):
    """Конфигурация Redis для Celery брокера"""

    REDIS_HOST: str = Field(
        description="Хост Redis"
    )
    REDIS_PORT: int = Field(
        description="Порт Redis"
    )
    REDIS_DB: int = Field(
        description="Номер базы данных Redis"
    )

    @property
    def url(self) -> str:
        """Получить URL подключения к Redis."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


redis_config = RedisConfig()
