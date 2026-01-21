"""
FastAPI приложение
"""


from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import api_router
from middleware import ExceptionHandlerMiddleware
from config import settings, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения."""
    yield


# Инициализируем FastAPI
app = FastAPI(
    title=settings.app_config.API_TITLE,
    description=settings.app_config.API_DESCRIPTION,
    version=settings.app_config.API_VERSION,
    docs_url="/docs" if settings.app_config.API_DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.app_config.API_DOCS_ENABLED else None,
    lifespan=lifespan,
)


# Инициализируем логгер
app_logger = setup_logging()

# Подключаем middleware для обработки исключений
if settings.monitoring_config.ENABLE_EXCEPTION_LOGGING:
    app.add_middleware(
        ExceptionHandlerMiddleware,
        logger=app_logger
    )


# Подключаем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API роутеры
app.include_router(api_router)
