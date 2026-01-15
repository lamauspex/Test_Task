
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)

from app.config import settings


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_async_db_session(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session


# Глобальный экземпляр
database_manager = DatabaseManager(settings.database.get_database_url())
get_async_db_session = database_manager.get_async_db_session
