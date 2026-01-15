""" Точка входа FastAPI приложения """

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения."""

    print("Инициализация базы данных...")
    # Инициализация БД происходит автоматически при первом подключении
    print("База данных готова")

    yield

    # Очистка ресурсов
    print("Приложение остановлено")


# Инициализируем FastAPI
app = FastAPI(
    title=settings.app.API_TITLE,
    description=settings.app.API_DESCRIPTION,
    version=settings.app.API_VERSION,
    docs_url="/docs" if settings.app.API_DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.app.API_DOCS_ENABLED else None,
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


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Crypto Price Tracker API",
        "version": settings.app.API_VERSION,
        "docs": "/docs" if settings.app.API_DOCS_ENABLED else "Disabled"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.monitoring.DEBUG
    )
