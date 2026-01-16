""" Базовый класс для всех моделей """


from sqlalchemy.orm import DeclarativeBase, declared_attr

from .mixin import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    UnixTimestampMixin
)


class Base(DeclarativeBase):
    """ Базовый класс для всех моделей SQLAlchemy """
    pass


class BaseModel(
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    UnixTimestampMixin
):
    """
    Базовый модель для всех моделей SQLAlchemy
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
