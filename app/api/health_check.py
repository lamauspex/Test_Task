"""
API маршруты для эндпоинтов данных о ценах.

Реализует обязательные GET методы с параметром тикера.
Вся обработка исключений и логирование вынесены в middleware.
"""

from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["Проверка"]
)


@router.get(
    "/",
    tags=["Здоровье"],
    summary="Проверка работоспособности",
    description="Простой эндпоинт для проверки работоспособности."
)
async def health_check() -> dict:
    """
    Эндпоинт проверки работоспособности.

    Returns:
        dict: Статус работоспособности
    """
    return {
        "status": "healthy",
        "timestamp": "2025-01-15T10:00:00Z"
    }
