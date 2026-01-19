""" Точка входа FastAPI приложения """

import uvicorn

from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app_config.HOST,
        port=settings.app_config.PORT,
        reload=settings.monitoring_config.DEBUG
    )
