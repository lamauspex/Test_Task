"""Единое место для всех зависимостей БД."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI — единственный источник БД-сессий.

    Yields:
        AsyncSession: Активная сессия базы данных
    """
    async with get_db_session() as session:
        yield session
