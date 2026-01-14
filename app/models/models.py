"""
Модели базы данных для приложения crypto price tracker
Использует SQLAlchemy с асинхронной поддержкой для PostgreSQL
"""

from decimal import Decimal
from app.models.models_base import BaseModel
from sqlalchemy import (
    DECIMAL,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)


class PriceRecord(BaseModel):
    """
    Модель для хранения записей цен криптовалют

    Атрибуты:

        ticker: Пара криптовалют (btc_usd, eth_usd)
        price: Текущая цена на момент получения
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    price: Mapped[Decimal] = mapped_column(
        DECIMAL(20, 8),
        nullable=False
    )
