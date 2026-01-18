""" Конфигурация Deribit API """

from pydantic import Field

from src.config.base import BaseConfig


class DeribitConfig(BaseConfig):
    """Конфигурация Deribit API"""

    # Публичный API не требует аутентификации
    CLIENT_ID: str = Field(
        default="",
        description="ID клиента Deribit (необязательно для public API)"
    )
    CLIENT_SECRET: str = Field(
        default="",
        description="Секрет клиента Deribit (необязательно для public API)"
    )
    API_URL: str = Field(
        default="https://www.deribit.com/api/v2/public",
        description="Базовый URL Deribit API",
        alias="DERIBIT_API_URL"
    )


deribit_config = DeribitConfig()
