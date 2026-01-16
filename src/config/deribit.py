""" Конфигурация Deribit API """

from pydantic import Field

from src.config.base import BaseConfig


class DeribitConfig(BaseConfig):
    """Конфигурация Deribit API"""

    CLIENT_ID: str = Field(
        description="ID клиента Deribit"
    )
    CLIENT_SECRET: str = Field(
        description="Секрет клиента Deribit"
    )
    DERIBIT_API_URL: str = Field(
        description="URL Deribit API"
    )


deribit_config = DeribitConfig()
