"""
Eдиное место для всех зависимостей БД
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_async_db_session


async def get_db() -> AsyncSession:
    """Dependency для FastAPI - единственный источник БД-сессий"""
    async with get_async_db_session() as session:
        yield session
