"""Конфигурация CORS для FastAPI приложения."""

from typing import List

from pydantic import Field

from .base import BaseConfig


class CORSConfig(BaseConfig):
    """Конфигурация CORS."""

    ALLOWED_ORIGINS: List[str] = Field(
        description="писок разрешённых источников"
    )

    ALLOWED_METHODS: List[str] = Field(
        description="Разрешённые методы"
    )

    ALLOWED_HEADERS: List[str] = Field(
        description="Разрешённые заголовки"
    )

    ALLOW_CREDENTIALS: bool = Field(
        description="Разрешить credentials (куки, авторизация)"
    )


cors_config = CORSConfig()
