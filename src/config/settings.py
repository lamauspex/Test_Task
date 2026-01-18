"""
Центральный объект конфигурации для crypto price tracker
"""

from ..config import (
    redis_config,
    monitoring_config,
    deribit_config,
    database_config,
    celery_config,
    app_config
)


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
        self.redis = redis_config

        self._initialized = True


settings = Settings()
