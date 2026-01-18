from src.config import settings
from src.database.database import get_db_session
from sqlalchemy import text
import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from decimal import Decimal

from src.repositories.price_repository import PriceRepository
from src.services.price_service import PriceService
from clients.deribit_client import PriceData
from src.database.uow import UnitOfWork


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


class TestUnitOfWork:
    """Тесты для UnitOfWork."""

    @pytest.mark.asyncio
    async def test_uow_context_manager(self):
        """Тест контекстного менеджера UoW."""
        # Arrange
        mock_db_manager = Mock()
        mock_session = AsyncMock()
        mock_db_manager.get_async_db_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_db_manager.get_async_db_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )

        # Act
        async with UnitOfWork(mock_db_manager) as uow:
            # Assert
            assert uow._session is mock_session
            mock_db_manager.get_async_db_session.assert_called_once()

        # Проверяем cleanup
        mock_session.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_uow_rollback_on_error(self):
        """Тест rollback при ошибке."""
        # Arrange
        mock_db_manager = Mock()
        mock_session = AsyncMock()
        mock_db_manager.get_async_db_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_db_manager.get_async_db_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )

        # Act & Assert
        with pytest.raises(ValueError):
            async with UnitOfWork(mock_db_manager) as uow:
                raise ValueError("Test error")

        # Проверяем что был rollback
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_uow_commit_on_success(self):
        """Тест commit при успехе."""
        # Arrange
        mock_db_manager = Mock()
        mock_session = AsyncMock()
        mock_db_manager.get_async_db_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_db_manager.get_async_db_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )

        # Act
        async with UnitOfWork(mock_db_manager) as uow:
            await uow.commit()

        # Assert
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_uow_prices_repository(self):
        """Тест получения репозитория через UoW."""
        # Arrange
        mock_db_manager = Mock()
        mock_session = AsyncMock()
        mock_db_manager.get_async_db_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_session
        )
        mock_db_manager.get_async_db_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )

        # Act
        async with UnitOfWork(mock_db_manager) as uow:
            repo1 = uow.prices
            repo2 = uow.prices

            # Assert
            assert isinstance(repo1, PriceRepository)
            assert repo1 is repo2  # Lazy initialization, same instance


class TestPriceServiceWithUoW:
    """Тесты для PriceService с использованием UoW."""

    @pytest.mark.asyncio
    async def test_save_price_data_uses_uow(self):
        """Тест что сервис использует переданный UoW."""
        # Arrange
        mock_uow = Mock()
        mock_uow.prices.save_price_data = AsyncMock()

        mock_deribit_client = Mock()
        service = PriceService(deribit_client=mock_deribit_client)

        price_data = PriceData(
            ticker="btc_usd",
            price=50000.0,
            timestamp=1705000000
        )

        # Act
        await service.save_price_data(mock_uow, price_data)

        # Assert
        mock_uow.prices.save_price_data.assert_called_once_with(
            ticker="btc_usd",
            price=50000.0,
            timestamp=1705000000
        )

    @pytest.mark.asyncio
    async def test_fetch_and_save_all_prices_uses_uow(self):
        """Тест что fetch использует переданный UoW."""
        # Arrange
        mock_uow = Mock()
        mock_uow.prices.save_price_data = AsyncMock()

        mock_deribit_client = Mock()
        mock_deribit_client.fetch_all_prices = AsyncMock(return_value={
            "btc_usd": PriceData(ticker="btc_usd", price=50000.0, timestamp=1705000000),
            "eth_usd": PriceData(ticker="eth_usd", price=3000.0, timestamp=1705000000),
        })

        service = PriceService(deribit_client=mock_deribit_client)

        # Act
        result = await service.fetch_and_save_all_prices(mock_uow)

        # Assert
        assert result == ["btc_usd", "eth_usd"]
        assert mock_uow.prices.save_price_data.call_count == 2


""" Тест архитектуры репозиториев """


def test_database_connection():
    """Тест подключения к БД"""
    from src.config import settings
    assert settings.database.TESTING == True
    assert settings.database.DB_NAME == ":memory:"


def test_database_session():
    """Тест получения сессии БД"""
    from src.database.database import get_db_session
    from sqlalchemy import text
    with get_db_session() as session:
        assert session is not None
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1


def test_settings_structure():
    """Тест структуры настроек"""
    from src.config import settings
    assert hasattr(settings, 'database')
    assert hasattr(settings, 'monitoring')
    assert hasattr(settings, 'app')
    assert hasattr(settings, 'celery')
    assert hasattr(settings, 'deribit')


def test_monitoring_config():
    """Тест настроек мониторинга"""
    from src.config import settings
    assert hasattr(settings.monitoring, 'LOG_LEVEL')
    assert hasattr(settings.monitoring, 'DEBUG')


def test_app_config():
    """Тест настроек приложения"""
    from src.config import settings
    assert hasattr(settings.app, 'API_TITLE')
    assert hasattr(settings.app, 'API_VERSION')
    assert hasattr(settings.app, 'API_DOCS_ENABLED')


def test_database_config():
    """Тест настроек БД"""
    from src.config import settings
    assert hasattr(settings.database, 'get_database_url')
    url = settings.database.get_database_url()
    assert url == "sqlite:///:memory:"


def test_celery_config():
    """Тест настроек Celery"""
    from src.config import settings
    assert hasattr(settings.celery, 'BROKER_URL')
    assert hasattr(settings.celery, 'RESULT_BACKEND')
    assert hasattr(settings.celery, 'REDIS_URL')


def test_deribit_config():
    """Тест настроек Deribit"""
    from src.config import settings
    assert hasattr(settings.deribit, 'CLIENT_ID')
    assert hasattr(settings.deribit, 'CLIENT_SECRET')
    assert hasattr(settings.deribit, 'API_URL')
