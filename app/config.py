"""Конфигурация приложения для crypto price tracker."""

import os
from typing import Any, Dict, Optional

from app.config.base import BaseConfig


class Settings(BaseConfig):
    """Настройки приложения."""

    def __init__(self) -> None:
        # Основные настройки базы данных
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///./crypto_prices.db"  # По умолчанию SQLite
        )

        # Настройки API
        self.api_host: str = os.getenv("API_HOST", "0.0.0.0")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))

        # Настройки Deribit API
        self.deribit_client_id: str = os.getenv("DERIBIT_CLIENT_ID", "")
        self.deribit_client_secret: str = os.getenv(
            "DERIBIT_CLIENT_SECRET", "")
        self.deribit_api_url: str = os.getenv(
            "DERIBIT_API_URL", "https://www.deribit.com/api/v2")

        # Настройки Celery (если используется)
        self.celery_broker_url: str = os.getenv(
            "CELERY_BROKER_URL", "redis://localhost:6379/0")
        self.celery_result_backend: str = os.getenv(
            "CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

        # Настройки логирования
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def model_dump(self) -> Dict[str, Any]:
        """Вернуть настройки в виде словаря."""
        return {
            "database_url": self.database_url,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "deribit_client_id": self.deribit_client_id,
            "deribit_client_secret": self.deribit_client_secret,
            "deribit_api_url": self.deribit_api_url,
            "celery_broker_url": self.celery_broker_url,
            "celery_result_backend": self.celery_result_backend,
            "log_level": self.log_level,
        }


# Глобальный инстанс настроек
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Получить инстанс настроек приложения.

    Returns:
        Settings: Инстанс настроек
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        print(f"Загружены настройки: database_url = {_settings.database_url}")
    return _settings


def reload_settings() -> None:
    """Перезагрузить настройки (полезно для тестов)."""
    global _settings
    _settings = None
