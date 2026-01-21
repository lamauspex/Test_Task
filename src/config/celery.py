""" Конфигурация Celery """

from pydantic import Field

from .base import BaseConfig
from .redis import redis_config


class CeleryConfig(BaseConfig):
    """ Конфигурация Celery """

    SCRIPT_LOCATION: str = Field(
        description="Путь к Celery приложению для запуска"
    )
    FETCH_INTERVAL: int = Field(
        description="Интервал получения цен в секундах"
    )

    # Настройки задачи fetch_crypto_prices
    FETCH_SOFT_TIME_LIMIT: int = Field(
        description="Tаймаут для задачи fetch_crypto_prices (сек)"
    )
    FETCH_RETRY_COUNTDOWN: int = Field(
        description="Задержка перед повтором fetch_crypto_prices (сек)"
    )
    FETCH_MAX_RETRIES: int = Field(
        description="Максимальное количество повторов fetch_crypto_prices"
    )

    @property
    def broker_url(self) -> str:
        """Получить URL брокера для Redis"""

        return redis_config.url

    @property
    def result_backend(self) -> str:
        """Получить URL бэкенда результатов для Redis"""

        # Берём base URL и меняем DB на +1
        base_url = redis_config.url.rsplit('/', 1)[0]
        return f"{base_url}/{redis_config.REDIS_DB + 1}"


celery_config = CeleryConfig()
