"""
Центральный объект конфигурации для crypto price tracker
"""

from .redis import RedisConfig
from .monitoring import MonitoringConfig
from .deribit import DeribitConfig
from .database import DataBaseConfig
from .celery import CeleryConfig
from .app import AppConfig


class Settings:
    """Центральный объект конфигурации"""

    def __init__(self):

        self.app = AppConfig()
        self.database = DataBaseConfig()
        self.monitoring = MonitoringConfig()
        self.celery = CeleryConfig()
        self.deribit = DeribitConfig()
        self.redis = RedisConfig()


def create_settings(**kwargs) -> Settings:
    """ Создаёт новый экземпляр """
    return Settings(**kwargs)
