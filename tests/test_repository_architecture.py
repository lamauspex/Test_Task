"""Пример теста с новой архитектурой Repository."""

from src.config import settings
from src.database.database import get_db_session
from sqlalchemy import text
import pytest
from unittest.mock import AsyncMock, Mock
from decimal import Decimal

from src.repositories.price_repository import PriceRepository
from src.services.price_service import PriceService
from src.clients.deribit_client import PriceData


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


""" Тест архитектуры репозиториев """


def test_database_connection():
    """Тест подключения к БД"""
    assert settings.database.TESTING == True
    assert settings.database.DB_NAME == ":memory:"


def test_database_session():
    """Тест получения сессии БД"""
    with get_db_session() as session:
        assert session is not None
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1


def test_settings_structure():
    """Тест структуры настроек"""
    assert hasattr(settings, 'database')
    assert hasattr(settings, 'monitoring')
    assert hasattr(settings, 'app')
    assert hasattr(settings, 'celery')
    assert hasattr(settings, 'deribit')


def test_monitoring_config():
    """Тест настроек мониторинга"""
    assert hasattr(settings.monitoring, 'LOG_LEVEL')
    assert hasattr(settings.monitoring, 'DEBUG')


def test_app_config():
    """Тест настроек приложения"""
    assert hasattr(settings.app, 'API_TITLE')
    assert hasattr(settings.app, 'API_VERSION')
    assert hasattr(settings.app, 'API_DOCS_ENABLED')


def test_database_config():
    """Тест настроек БД"""
    assert hasattr(settings.database, 'get_database_url')
    url = settings.database.get_database_url()
    assert url == "sqlite:///:memory:"


def test_celery_config():
    """Тест настроек Celery"""
    assert hasattr(settings.celery, 'BROKER_URL')
    assert hasattr(settings.celery, 'RESULT_BACKEND')
    assert hasattr(settings.celery, 'REDIS_URL')


def test_deribit_config():
    """Тест настроек Deribit"""
    assert hasattr(settings.deribit, 'CLIENT_ID')
    assert hasattr(settings.deribit, 'CLIENT_SECRET')
    assert hasattr(settings.deribit, 'API_URL')
