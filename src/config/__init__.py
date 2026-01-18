"""
Конфигурация для Crypto Price Tracker

Использование:
    from src.config import settings  # единая точка входа
    from src.config import database_config  # или отдельный конфиг
"""
from .settings import settings
from .app import app_config
from .base import BaseConfig
from .celery import celery_config, celery_app
from .database import database_config
from .deribit import deribit_config
from .monitoring import monitoring_config
from .redis import redis_config
from .logging import setup_logging


__all__ = [
    'settings',
    'app_config',
    'BaseConfig',
    'celery_config',
    'celery_app',
    'database_config',
    'deribit_config',
    'monitoring_config',
    'redis_config',
    'setup_logging'
]
