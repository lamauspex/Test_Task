"""
API router module
"""
from fastapi import APIRouter

# Импортируем все роутеры
from .routes import router


# Создаем главный API router
api_router = APIRouter(prefix="/api")

# Подключаем все роутеры с префиксами
api_router.include_router(router)

__all__ = ["router", "api_router"]
