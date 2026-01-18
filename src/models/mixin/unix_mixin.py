"""Миксины для моделей"""

from sqlalchemy import BigInteger
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)


class UnixTimestampMixin:
    """Миксин для добавления UNIX timestamp."""

    timestamp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment='UNIX timestamp цены'
    )
