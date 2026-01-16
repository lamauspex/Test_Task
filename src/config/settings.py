"""
Центральный объект конфигурации для crypto price tracker
"""

from .app import app_config
from .celery import celery_config
from .database import database_config
from .deribit import deribit_config
from .monitoring import monitoring_config


class _SettingsHolder:
    """ Холдер для синглтона """

    instance = None


class Settings:
    """Центральный объект конфигурации"""

    def __new__(cls):
        if _SettingsHolder.instance is None:
            _SettingsHolder.instance = super().__new__(cls)
            _SettingsHolder.instance._initialized = False
        return _SettingsHolder.instance

    def __init__(self):
        # Инициализируем только один раз
        if self._initialized:
            return

        self.app = app_config
        self.database = database_config
        self.monitoring = monitoring_config
        self.celery = celery_config
        self.deribit = deribit_config

        self._initialized = True


settings = Settings()
