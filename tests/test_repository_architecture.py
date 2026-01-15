"""Пример теста с новой архитектурой Repository."""

import pytest
from unittest.mock import AsyncMock, Mock
from decimal import Decimal

from app.repositories.price_repository import PriceRepository
from app.services.price_service import PriceService
from clients.deribit_client import PriceData


class TestPriceRepository:
    """Тесты для PriceRepository."""

    @pytest.mark.asyncio
    async def test_save_price_data(self):
        """Тест сохранения данных о цене."""
        # Arrange
        mock_session = AsyncMock()
        repository = PriceRepository(mock_session)

        # Act
        await repository.save_price_data("btc_usd", 50000.0, 1705000000)

        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_price(self):
        """Тест получения последней цены."""
        # Arrange
        mock_session = AsyncMock()
        mock_record = Mock()
        mock_record.ticker = "btc_usd"
        mock_record.price = Decimal("50000.0")
        mock_record.timestamp = 1705000000

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_record
        mock_session.execute.return_value = mock_result

        repository = PriceRepository(mock_session)

        # Act
        result = await repository.get_latest_price("btc_usd")

        # Assert
        assert result == mock_record
        mock_session.execute.assert_called_once()


class TestPriceServiceWithRepository:
    """Тесты для PriceService с использованием репозитория."""

    @pytest.mark.asyncio
    async def test_save_price_data_uses_repository(self):
        """Тест что сервис использует репозиторий."""
        # Arrange
        mock_database = Mock()
        mock_session = AsyncMock()
        mock_database.get_session.return_value.__aenter__.return_value = mock_session
        mock_database.get_session.return_value.__aexit__.return_value = None

        mock_deribit_client = Mock()

        service = PriceService(
            database=mock_database,
            deribit_client=mock_deribit_client
        )

        price_data = PriceData(
            ticker="btc_usd",
            price=50000.0,
            timestamp=1705000000
        )

        # Act
        await service.save_price_data(price_data)

        # Assert
        # Проверяем что создалась сессия
        mock_database.get_session.assert_called_once()
        # Проверяем что данные сохранились
        mock_session.commit.assert_called_once()
