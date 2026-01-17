"""
Настройка структурированного логирования
"""

import sys
import logging

from src.config import settings


def setup_logging() -> logging.Logger:
    """Настройка структурированного логирования для контейнера."""

    log_level = getattr(
        logging, settings.monitoring.LOG_LEVEL.upper(),
        logging.INFO
    )
    log_format = settings.monitoring.LOG_FORMAT

    # Очищаем существующие handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Создаём handler для stdout (Docker собирает эти логи)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if log_format == "json" and settings.monitoring.STRUCTURED_LOGGING:

        # Используем стандартный формат для JSON
        handler.setFormatter(
            logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"name": "%(name)s", "message": "%(message)s"}'
            )
        )
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    return logging.getLogger(__name__)
