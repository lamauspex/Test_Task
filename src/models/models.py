"""Модели базы данных для приложения crypto price tracker."""

from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .models_base import BaseModel


class PriceRecord(BaseModel):
    """Модель для хранения записей цен криптовалют."""

    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    price: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8),
        nullable=False
    )
