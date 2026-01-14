"""Параметры запросов."""


from pydantic import Field, field_validator

from app.schemas import TickerQueryParams


class DateRangeQueryParams(TickerQueryParams):
    """
    Параметры запроса с фильтром по диапазону дат.
    Расширяет валидацию тикера параметрами диапазона дат.
    """

    start_date: int = Field(
        ...,
        ge=0,
        description="Начальная дата как UNIX timestamp"
    )
    end_date: int = Field(
        ...,
        ge=0,
        description="Конечная дата как UNIX timestamp"
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: int, info) -> int:
        """Убедиться, что end_date больше или равен start_date."""

        start = info.data.get("start_date", 0)
        if v < start:
            raise ValueError(
                "end_date должен быть больше или равен start_date"
            )
        return v
