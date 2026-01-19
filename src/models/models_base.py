"""Базовые классы моделей SQLAlchemy."""

from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr
)

from .mixin import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    UnixTimestampMixin
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


class BaseModel(
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    UnixTimestampMixin
):
    """Базовый модель с предустановленными миксинами"""

    __abstract__ = True

    @declared_attr  # type: ignore[override]
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
