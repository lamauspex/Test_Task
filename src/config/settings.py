"""
Центральный объект конфигурации для crypto price tracker
"""

from ..config import (
    RedisConfig,
    MonitoringConfig,
    DeribitConfig,
    DataBaseConfig,
    CeleryConfig,
    AppConfig
)


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
