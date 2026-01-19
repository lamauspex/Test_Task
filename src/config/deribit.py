""" Конфигурация Deribit API """

from pydantic import Field

from .base import BaseConfig


class DeribitConfig(BaseConfig):
    """Конфигурация Deribit API"""

    # Публичный API не требует аутентификации
    CLIENT_ID: str = Field(
        description="ID клиента Deribit"
    )
    CLIENT_SECRET: str = Field(
        description="Секрет клиента Deribit"
    )
    DERIBIT_API_URL: str = Field(
        description="Базовый URL Deribit API",
    )


derbit_config = DeribitConfig()
