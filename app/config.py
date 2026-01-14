"""
Модуль конфигурации для приложения crypto price tracker.

Использует Pydantic Settings для управления переменными окружения.
Паттерн: lazy loading через lru_cache без глобальных переменных.
"""
from functools import lru_cache
from typing import Tuple

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения.

    Все настройки определены как атрибуты класса с умолчательными значениями.
    Загрузка происходит лениво через get_settings().
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Настройки базы данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_prices"

    # Настройки Redis
    redis_url: str = "redis://localhost:6379/0"

    # Настройки Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    fetch_interval: int = 60  # секунды

    # Настройки Deribit API
    deribit_api_url: str = "https://www.deribit.com/api/v2/public/get_index_price"

    # Настройки приложения
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Допустимые тикеры для валидации
    @property
    def valid_tickers(self) -> Tuple[str, str]:
        """Возвращает кортеж допустимых тикеров."""
        return ("btc_usd", "eth_usd")


@lru_cache()
def get_settings() -> Settings:
    """
    Получить кэшированный экземпляр настроек.

    Использование lru_cache гарантирует:
    - Создание одного экземпляра (кеширование)
    - Отсутствие глобальной переменной
    - Ленивую загрузку (создание при первом вызове)

    Returns:
        Settings: Экземпляр конфигурации приложения
    """
    return Settings()
