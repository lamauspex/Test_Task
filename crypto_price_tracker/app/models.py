"""
Модели базы данных для приложения crypto price tracker
Использует SQLAlchemy с асинхронной поддержкой для PostgreSQL
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    DateTime,
    DECIMAL,
    Index,
    Integer,
    String,
    BigInteger,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)


class Base(DeclarativeBase):
    """ Базовый класс для всех моделей SQLAlchemy """
    pass


class PriceRecord(Base):
    """
    Модель для хранения записей цен криптовалют

    Атрибуты:
        id: Первичный ключ
        ticker: Пара криптовалют (btc_usd, eth_usd)
        price: Текущая цена на момент получения
        timestamp: UNIX timestamp цены
        created_at: Timestamp вставки в базу данных
    """
    __tablename__ = "price_records"

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
    timestamp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Составной индекс для эффективных запросов по тикеру и диапазону времени
    __table_args__ = (
        Index(
            "ix_price_records_ticker_timestamp",
            "ticker",
            "timestamp"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<PriceRecord(id={self.id}, ticker={self.ticker}, "
            f"price={self.price}, timestamp={self.timestamp})>"
        )
