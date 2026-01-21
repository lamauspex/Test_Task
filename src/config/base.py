""" Базовые классы для конфигурации """


from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class BaseConfig(BaseSettings):
    """
    Базовый класс конфигурации
    с поддержкой переменных окружения Docker
    """

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra='ignore',
        env_prefix='',
        env_file=None,
    )
