"""Тесты валидации через Pydantic схемы."""

import pytest
from src.schemas.requests import (
    AllPricesQuery,
    LatestPriceQuery,
    DateRangePricesQuery
)


class TestValidation:
    """Класс для тестов валидации схем."""

    def test_all_prices_query_validation(self):
        """Тест валидации AllPricesQuery."""
        query = AllPricesQuery(ticker='btc_usd', limit=100, offset=0)
        assert query.ticker == 'btc_usd'
        assert query.limit == 100
        assert query.offset == 0

    def test_latest_price_query_invalid_ticker(self):
        """Тест валидации LatestPriceQuery с неверным тикером."""
        with pytest.raises(Exception):
            LatestPriceQuery(ticker='invalid_ticker')

    def test_date_range_prices_query_validation(self):
        """Тест валидации DateRangePricesQuery."""
        query = DateRangePricesQuery(
            ticker='eth_usd',
            start_date=1704067200,
            end_date=1704153600,
            limit=500
        )
        assert query.ticker == 'eth_usd'
        assert query.start_date == 1704067200
        assert query.end_date == 1704153600
        assert query.limit == 500

    def test_date_range_prices_query_invalid_range(self):
        """Тест валидации DateRangePricesQuery с неверным диапазоном."""
        with pytest.raises(Exception):
            DateRangePricesQuery(
                ticker='btc_usd',
                start_date=1704153600,  # start > end
                end_date=1704067200,
                limit=500
            )
