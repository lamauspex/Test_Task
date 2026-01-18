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

    def get_database_url(
        self,
        driver: str = "postgresql+asyncpg"
    ) -> str:
        """
        Получить URL базы данных с указанным драйвером

        Args:
            driver: Драйвер базы данных

        Returns:
            Сформированный URL базы данных
        """

        return (
            f"{driver}://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
