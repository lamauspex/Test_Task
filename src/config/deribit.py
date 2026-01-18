""" Конфигурация Deribit API """

from pydantic import Field

from .base import BaseConfig


class DeribitConfig(BaseConfig):
    """Конфигурация Deribit API"""

    # Публичный API не требует аутентификации
    CLIENT_ID: str = Field(
        description="ID клиента Deribit (необязательно для public API)"
    )
    CLIENT_SECRET: str = Field(
        description="Секрет клиента Deribit (необязательно для public API)"
    )
    API_URL: str = Field(
        description="Базовый URL Deribit API",
        alias="DERIBIT_API_URL"
    )
