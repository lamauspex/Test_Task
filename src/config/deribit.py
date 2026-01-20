""" Конфигурация Deribit API """

from pydantic import Field

from .base import BaseConfig


class DeribitConfig(BaseConfig):
    """Конфигурация Deribit API"""

    DERIBIT_API_URL: str = Field(
        description="Базовый URL Deribit API",
    )


derbit_config = DeribitConfig()
