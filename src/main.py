"""Точка входа FastAPI приложения."""

import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.monitoring.DEBUG
    )
