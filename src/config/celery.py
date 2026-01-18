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

    # Настройки задачи fetch_crypto_prices
    FETCH_SOFT_TIME_LIMIT: int = Field(
        default=55,
        description="Мягкий таймаут для задачи fetch_crypto_prices (сек)"
    )
    FETCH_RETRY_COUNTDOWN: int = Field(
        default=60,
        description="Задержка перед повтором fetch_crypto_prices (сек)"
    )
    FETCH_MAX_RETRIES: int = Field(
        default=3,
        description="Максимальное количество повторов fetch_crypto_prices"
    )

    @property
    def broker_url(self) -> str:
        """Получить URL брокера для Redis."""
        return redis_config.url

    @property
    def result_backend(self) -> str:
        """Получить URL бэкенда результатов для Redis"""

        return (
            f"redis://{redis_config.HOST}:"
            f"{redis_config.PORT}/{redis_config.DB + 1}"
        )


__all__ = ['CeleryConfig']
