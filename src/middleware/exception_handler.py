"""Middleware для обработки исключений """

import logging
import traceback
from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from config import create_settings
from schemas import ErrorResponse
from exceptions import PriceNotFoundError


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для централизованной обработки исключений."""

    def __init__(self, app: FastAPI, logger: logging.Logger | None = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)
        self.enabled = create_settings.monitoring.ENABLE_EXCEPTION_LOGGING

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Any]
    ) -> Response:
        """Обработка всех исключений."""

        if not self.enabled:
            return await call_next(request)

        try:
            return await call_next(request)
        except PriceNotFoundError as e:
            self.logger.warning(f"Price not found: {e.ticker}")
            return JSONResponse(
                status_code=404,
                content={"detail": str(e)}
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
