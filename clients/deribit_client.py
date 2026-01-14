"""
Клиент API Deribit с использованием aiohttp для асинхронных HTTP-запросов.

Получает индексные цены для BTC/USD и ETH/USD.
"""
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Protocol, runtime_checkable

import aiohttp

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Датакласс для информации о цене."""
    ticker: str
    price: Decimal
    timestamp: int


class DeribitClientError(Exception):
    """Исключение, выбрасываемое при ошибках API Deribit."""


@runtime_checkable
class IDeribitClient(Protocol):
    """Протокол (интерфейс) клиента Deribit для тестирования и мокинга."""

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """Получить цены для всех поддерживаемых тикеров."""
        ...


class DeribitClient:
    """
    Асинхронный клиент для API Deribit.

    Использует aiohttp для неблокирующих HTTP-запросов.
    Не использует синглтон - создаётся через фабрику или DI.

    Attributes:
        api_url: URL эндпоинта API Deribit
        timeout: Таймаут для HTTP запросов
    """

    def __init__(
        self,
        settings: Settings | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """
        Инициализация клиента.

        Args:
            settings: Настройки приложения. Если None - загружаются из окружения.
            session: Сессия aiohttp. Если None - создаётся новая.
        """
        self._settings = settings or get_settings()
        self._api_url = self._settings.deribit_api_url
        self._session = session

    @property
    def api_url(self) -> str:
        """Получить URL API."""
        return self._api_url

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """
        Получить или создать сессию aiohttp.

        Returns:
            aiohttp.ClientSession: HTTP сессия
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
        return self._session

    async def _fetch_price(self, ticker: str) -> PriceData:
        """
        Получить цену для одного тикера.

        Args:
            ticker: Пара криптовалют (btc_usd или eth_usd)

        Returns:
            PriceData: Информация о цене

        Raises:
            DeribitClientError: Если запрос к API неудачен
        """
        session = await self._ensure_session()

        # Преобразование формата тикера для API Deribit
        deribit_ticker = ticker.replace("_", "-")

        params = {"index_name": deribit_ticker}

        try:
            async with session.get(self._api_url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка API Deribit для {ticker}: "
                        f"status={response.status}, body={error_text}"
                    )
                    raise DeribitClientError(
                        f"API вернул статус {response.status}: {error_text}"
                    )

                data = await response.json()

                # Разбор ответа согласно формату API Deribit
                result = data.get("result", {})
                if not result:
                    logger.error(f"Пустой результат от Deribit для {ticker}")
                    raise DeribitClientError(
                        f"Пустой результат для тикера: {ticker}"
                    )

                price = Decimal(str(result.get("index_price", 0)))
                # Конвертация миллисекунд в секунды
                timestamp = int(result.get("timestamp", 0)) // 1000

                return PriceData(
                    ticker=ticker,
                    price=price,
                    timestamp=timestamp
                )

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при получении {ticker}: {e}")
            raise DeribitClientError(f"Ошибка сети: {e}")

    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        """
        Получить цены для всех поддерживаемых тикеров.

        Получает цены BTC/USD и ETH/USD одновременно.

        Returns:
            Dict[str, PriceData]: Словарь {тикер: данные о цене}
        """
        import asyncio

        tickers = ["btc_usd", "eth_usd"]
        prices: Dict[str, PriceData] = {}

        # Получение всех цен одновременно
        tasks = [self._fetch_price(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for ticker, result in zip(tickers, results):
            if isinstance(result, Exception):
                logger.error(f"Не удалось получить {ticker}: {result}")
            else:
                prices[ticker] = result
                logger.info(
                    f"Получено {ticker}: price={result.price}, "
                    f"timestamp={result.timestamp}"
                )

        return prices

    async def close(self) -> None:
        """
        Закрыть сессию aiohttp.

        Вызывается при завершении работы приложения.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "DeribitClient":
        """Контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        await self.close()
