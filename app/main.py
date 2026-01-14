"""
Точка входа FastAPI приложения.

Создаёт и настраивает приложение FastAPI с lifespan.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import get_database
from app.api.routes import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.

    Инициализирует базу данных при запуске и закрывает соединения при завершении.

    Args:
        app: Экземпляр FastAPI
    """
    # Запуск
    logger.info("Запуск приложения...")

    # Инициализация базы данных
    db = get_database()
    await db.init()
    logger.info("База данных инициализирована")

    # Создание таблиц
    await db.create_tables()
    logger.info("Таблицы базы данных созданы")

    yield

    # Завершение работы
    logger.info("Завершение работы приложения...")
    await db.close()
    logger.info("Соединения с базой данных закрыты")


def create_app() -> FastAPI:
    """
    Создать и настроить экземпляр FastAPI.

    Returns:
        FastAPI: Настроенное приложение
    """
    settings = get_settings()

    app = FastAPI(
        title="Crypto Price Tracker API",
        description=(
            "API для отслеживания цен криптовалют с биржи Deribit. "
            "Предоставляет методы для получения исторических и текущих цен."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение маршрутов
    app.include_router(router)

    # Эндпоинт проверки работы
    @app.get("/")
    async def root() -> dict:
        """Корневой эндпоинт."""
        return {
            "name": "Crypto Price Tracker API",
            "version": "1.0.0",
            "status": "running"
        }

    return app


# Создание экземпляра приложения
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
