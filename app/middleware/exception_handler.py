"""Middleware для обработки исключений и логирования."""

from typing import Any, Callable
import logging
import traceback
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas.responses import ErrorResponse


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для централизованной обработки исключений."""

    def __init__(self, app: FastAPI, logger: logging.Logger | None = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """Обработка всех исключений."""
        try:
            return await call_next(request)
        except ValueError as e:
            # Ошибки валидации данных
            self.logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(detail=str(e)).model_dump()
            )
        except KeyError as e:
            # Отсутствующие ключи
            self.logger.warning(f"Key error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    detail=f"Missing required parameter: {str(e)}").model_dump()
            )
        except Exception as e:
            # Непредвиденные ошибки
            self.logger.error(
                f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    detail="Internal server error").model_dump()
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов."""

    def __init__(self, app: FastAPI, logger: logging.Logger | None = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """Логирование входящих запросов."""
        # Логирование входящего запроса
        self.logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )

        # Выполнение запроса
        response = await call_next(request)

        # Логирование ответа
        self.logger.info(
            f"Response: {response.status_code} - "
            f"Path: {request.url.path}"
        )

        return response
