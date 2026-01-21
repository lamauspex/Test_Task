""" Конфигурация БД """


from pydantic import Field

from .base import BaseConfig


class DataBaseConfig(BaseConfig):
    """ Конфигурация БД """

    # БАЗА ДАННЫХ
    DB_USER: str = Field(description="Пользователь")
    DB_HOST: str = Field(description="Хост БД")
    DB_PORT: int = Field(description="Порт БД")
    DB_NAME: str = Field(description="Название БД")
    DB_PASSWORD: str = Field(description="Пароль БД")
    DB_DRIVER: str = Field(description="Драйвер БД")

    def get_database_url(self) -> str:
        """
        Получить URL базы данных с указанным драйвером
        """

        return (
            f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


data_config = DataBaseConfig()
