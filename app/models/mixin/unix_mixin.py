

from sqlalchemy import BigInteger
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)


class UnixTimestampMixin:

    timestamp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment='UNIX timestamp цены'
    )
