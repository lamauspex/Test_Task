"""
Модуль конфигурации для приложения crypto price tracker.

Использует Pydantic Settings для управления переменными окружения.
Паттерн: lazy loading через lru_cache без глобальных переменных.
"""

import os
from typing import List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Настройки приложения."""

    # API настройки
    app_host: str = Field(
        default="0.0.0.0", description="Хост для запуска приложения")
    app_port: int = Field(
        default=8000, description="Порт для запуска приложения")
    app_title: str = Field(
        default="Crypto Price Tracker API", description="Заголовок API")
    app_version: str = Field(default="1.0.0", description="Версия API")

    # База данных
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/crypto_tracker",
        description="URL подключения к базе данных"
    )

    # Deribit API
    deribit_base_url: str = Field(
        default="https://www.deribit.com/api/v2",
        description="Базовый URL Deribit API"
    )
    deribit_timeout: int = Field(
        default=30, description="Таймаут для запросов к Deribit")

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL брокера для Celery"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="URL бэкенда результатов для Celery"
    )

    # Валидные тикеры
    valid_tickers: List[str] = Field(
        default=["btc_usd", "eth_usd"],
        description="Список валидных тикеров криптовалют"
    )

    # Настройки логирования
    log_level: str = Field(default="INFO", description="Уровень логирования")

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Получить экземпляр настроек."""
    return Settings()
