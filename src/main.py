""" Точка входа FastAPI приложения """

import uvicorn

from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.monitoring.DEBUG
    )
