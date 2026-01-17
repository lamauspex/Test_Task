"""
API router module
"""
from fastapi import APIRouter

# Импортируем все роутеры
from src.api.routes import router as price_tracker_router


# Создаем главный API router
api_router = APIRouter(prefix="/api")

# Подключаем все роутеры с префиксами
api_router.include_router(price_tracker_router)
