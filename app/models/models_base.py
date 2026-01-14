""" Базовый класс для всех моделей """


from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Index

from app.models.mixin.time_mixin import (
    TimestampMixin,
    UUIDPrimaryKeyMixin
)


class Base(DeclarativeBase):
    """ Базовый класс для всех моделей SQLAlchemy """
    pass


class BaseModel(
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin
):
    """
    Базовый модель для всех моделей SQLAlchemy
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

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
