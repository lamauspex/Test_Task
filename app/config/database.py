""" Конфигурация БД """


from pydantic import Field

from app.config.base import BaseConfig


class DataBaseConfig(BaseConfig):
    """ Конфигурация БД """

    # БАЗА ДАННЫХ (ОБЩИЕ НАСТРОЙКИ)
    DB_USER: str = Field(description="Пользователь")
    DB_HOST: str = Field(description="Хост БД")
    DB_PORT: int = Field(description="Порт БД")
    DB_NAME: str = Field(description="Название БД")
    DB_PASSWORD: str = Field(description="Пароль БД")

    # ОКРУЖЕНИЕ И РЕЖИМ ОТЛАДКИ
    TESTING: bool = Field(description="Тестирование")
    DEBUG: bool = Field(description="Режим отладки")

    def get_database_url(
        self,
        driver: str = "postgresql+psycopg2"
    ) -> str:
        """
        Получить URL базы данных с указанным драйвером

        Args:
            driver: Драйвер базы данных
            (по умолчанию postgresql+psycopg2)

        Returns:
            Сформированный URL базы данных
        """

        if self.TESTING:
            return "sqlite:///:memory:"

        return (
            f"{driver}://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


database_config = DataBaseConfig()
