"""HTTP-клиент для Deribit API."""

import logging
from typing import Optional

import aiohttp

from src.config.settings import settings
from src.exceptions.exceptions import DeribitClientError


logger = logging.getLogger(__name__)


class DeribitHttpClient:
    """
    HTTP-клиент для Deribit API.

    Отвечает только за управление сессией и выполнение HTTP-запросов.
    """

    def __init__(
        self,
        settings_obj=None,
        session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        """Инициализация HTTP-клиента."""
        self._settings = settings_obj or settings.deribit
        self._session = session

    @property
    def api_url(self) -> str:
        """Получить базовый URL API."""
        return self._settings.API_URL

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Убедиться, что сессия существует."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Закрыть сессию, если она была создана."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None
    ) -> dict:
        """
        Выполнить HTTP-запрос к Deribit API.

        Args:
            method: HTTP-метод
            endpoint: Эндпоинт API
            params: Параметры запроса

        Returns:
            dict: Ответ от API

        Raises:
            DeribitClientError: При ошибке запроса
        """
        url = f"{self.api_url}{endpoint}"

        try:
            session = await self._ensure_session()

            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Deribit API error: status={response.status}, "
                        f"body={error_text}"
                    )
                    raise DeribitClientError(
                        f"API returned status {response.status}"
                    )

                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise DeribitClientError(f"Network error: {e}")

    async def __aenter__(self) -> "DeribitHttpClient":
        """Контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        await self.close()
