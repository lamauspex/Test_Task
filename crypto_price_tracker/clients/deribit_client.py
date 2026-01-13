"""
Клиент API Deribit с использованием aiohttp для асинхронных HTTP-запросов.

Получает индексные цены для BTC/USD и ETH/USD.
"""
import asyncio
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

import aiohttp

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Датакласс для информации о цене."""
    ticker: str
    price: Decimal
    timestamp: int


class DeribitClientError(Exception):
    """Исключение, выбрасываемое при ошибках API Deribit."""
    pass


class DeribitClient:
    """
    Асинхронный клиент для API Deribit.

    Использует aiohttp для неблокирующих HTTP-запросов.
    Реализует паттерн синглтона для эффективного использования ресурсов.
    """

    _instance: Optional["DeribitClient"] = None
    _session: Optional[aiohttp.ClientSession] = None

    def __new__(cls) -> "DeribitClient":
        """
        Реализация паттерна синглтона.

        Returns:
            DeribitClient: Одиночный экземпляр клиента
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Инициализация клиента с настройками."""
        self._settings = get_settings()
        self._api_url = self._settings.deribit_api_url

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получить или создать сессию aiohttp.

        Сессия используется повторно для эффективности пула соединений.

        Returns:
            aiohttp.ClientSession: HTTP сессия

        Raises:
            DeribitClientError: Если создание сессии не удалось
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
        session = await self._get_session()

        # Преобразование формата тикера для API Deribit
        deribit_ticker = ticker.replace("_", "-")

        params = {"index_name": deribit_ticker}

        try:
            async with session.get(
                self._api_url,
                params=params
            ) as response:
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
                        f"Пустой результат для тикера: {ticker}")

                price = Decimal(str(result.get("index_price", 0)))
                # Конвертация в секунды
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
            Dict[str, PriceData]: Словарь, связывающий тикер с данными о цене
        """
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

        Должен вызываться при завершении работы приложения.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


# Импорт asyncio для gather

# Синглтон экземпляр для использования в приложении
deribit_client = DeribitClient()
