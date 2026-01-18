"""  Конфигурация мониторинга и логирования """


from pydantic import Field

from src.config.base import BaseConfig


class MonitoringConfig(BaseConfig):
    """Конфигурация мониторинга и логирования"""

    # ЛОГИРОВАНИЕ
    LOG_LEVEL: str = Field(
        description="Уровень логирования"
    )
    LOG_FORMAT: str = Field(
        description="Формат логов"
    )
    STRUCTURED_LOGGING: bool = Field(
        description="Структурированное логирование"
    )
    ENABLE_REQUEST_LOGGING: bool = Field(
        description="Включить логи запросов"
    )
    ENABLE_EXCEPTION_LOGGING: bool = Field(
        description="Включить логи ошибок"
    )
    ENABLE_BUSINESS_LOGGING: bool = Field(
        description="Включить логи бизнес-логики"
    )

    # ОКРУЖЕНИЕ
    DEBUG: bool = Field(description="Режим отладки")


__all__ = ['MonitoringConfig']
