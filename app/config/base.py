""" Базовый конфигурационный класс """


from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """ Базовый конфигурационный класс """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore',
        validate_assignment=True,
    )
