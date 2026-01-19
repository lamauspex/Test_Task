"""
Центральный объект конфигурации для crypto price tracker
"""

from .deribit import derbit_config
from .monitoring import monitoring_config
from .celery import celery_config
from .redis import redis_config
from .database import data_config
from .app import app_config


class Settings:
    """Центральный объект конфигурации"""

    def __init__(self):

        self.app = app_config
        self.database = data_config
        self.monitoring = monitoring_config
        self.celery = celery_config
        self.deribit = derbit_config
        self.redis = redis_config


settings = Settings()
