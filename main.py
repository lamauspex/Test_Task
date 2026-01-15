"""
Точка входа FastAPI приложения.

Настраивает приложение, подключает middleware, роуты и обработчики.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config.config import get_settings
from app.database.database import get_database
from app.middleware.exception_handler import (
    ExceptionHandlerMiddleware,
    LoggingMiddleware
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения."""
    settings = get_settings()

    # Инициализация базы данных
    print("Инициализация базы данных...")
    db = get_database()
    await db.init(settings.database_url)
    await db.create_tables()
    print("База данных инициализирована")

    yield

    # Очистка ресурсов
    print("Закрытие подключений к базе данных...")
    await db.close()
    print("Приложение остановлено")


# Создание приложения FastAPI
app = FastAPI(
    title="Crypto Price Tracker API",
    description="API для получения данных о ценах криптовалют с биржи Deribit",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение middleware
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(router)


@app.get("/")
async def root() -> dict:
    """Корневой эндпоинт."""
    return {
        "message": "Crypto Price Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
