"""
Централизованная настройка логирования.

Использование:
    from config.logging import setup_logger, get_logger

    # Быстрый способ
    logger = setup_logger()

    # Или получить именованный логгер
    logger = get_logger(__name__)
"""

import sys
import logging
from typing import Optional

from .settings import create_settings


def setup_logger(
    name: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Настройка структурированного логирования.

    Args:
        name: Имя логгера. Если None - root logger.
        level: Уровень логирования. Берется из settings если None.

    Returns:
        Настроенный логгер
    """
    log_level = getattr(
        logging, (level or create_settings.monitoring.LOG_LEVEL).upper(),
        logging.INFO
    )
    log_format = create_settings.monitoring.LOG_FORMAT

    # Получаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Очищаем существующие handlers
    logger.handlers.clear()

    # Создаём handler для stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if log_format == "json" and create_settings.monitoring.STRUCTURED_LOGGING:
        handler.setFormatter(
            logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"name": "%(name)s", "message": "%(message)s"}'
            )
        )
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

    logger.addHandler(handler)
    return logger


def get_logger(name: str) -> logging.Logger:
    """ Получить настроенный логгер по имени """
    return setup_logger(name)


# Для обратной совместимости
def setup_logging() -> logging.Logger:
    """Настройка root логгера"""
    return setup_logger()
