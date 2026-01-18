""" Точка входа FastAPI приложения """

import uvicorn

from src.config import create_settings

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=create_settings.app.HOST,
        port=create_settings.app.PORT,
        reload=create_settings.monitoring.DEBUG
    )
