"""
API router module
"""
from fastapi import APIRouter

# Импортируем все роутеры
from app.api.health_check import router as health_check_router
from app.api.routes import router as price_tracker_router


# Создаем главный API router
api_router = APIRouter(prefix="/api/v1/prices")


# Подключаем все роутеры с префиксами
api_router.include_router(price_tracker_router)
api_router.include_router(health_check_router)
