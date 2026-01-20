"""Единое место для всех зависимостей БД."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .database import database_manager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI — единственный источник БД-сессий.

    Yields:
        AsyncSession: Активная сессия базы данных
    """
    async with database_manager.session_factory() as session:
        yield session
