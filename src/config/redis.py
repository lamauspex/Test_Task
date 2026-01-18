""" Конфигурация Redis """

from pydantic import Field

from src.config.base import BaseConfig


class RedisConfig(BaseConfig):
    """Конфигурация Redis для Celery брокера"""

    HOST: str = Field(
        default="localhost",
        description="Хост Redis"
    )
    PORT: int = Field(
        default=6379,
        description="Порт Redis"
    )
    DB: int = Field(
        default=0,
        description="Номер базы данных Redis"
    )

    @property
    def url(self) -> str:
        """Получить URL подключения к Redis."""
        return f"redis://{self.HOST}:{self.PORT}/{self.DB}"


__all__ = ['RedisConfig']
