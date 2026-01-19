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

    Deribit использует JSON-RPC 2.0 протокол.
    """

    def __init__(
        self,
        settings_obj=None,
        session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        """Инициализация HTTP-клиента."""
        self._settings = settings_obj or settings.deribit
        self._session = session
        self._request_id = 0

    @property
    def api_url(self) -> str:
        """Получить базовый URL API."""
        return self._settings.DERIBIT_API_URL

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Убедиться, что сессия существует."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Content-Type": "application/json"}
            )
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
        Выполнить JSON-RPC запрос к Deribit API.

        Args:
            method: Не используется (все запросы - POST)
            endpoint: JSON-RPC метод (например: public/get_index_price)
            params: Параметры запроса

        Returns:
            dict: Ответ от API

        Raises:
            DeribitClientError: При ошибке запроса
        """
        url = f"{self.api_url}{endpoint}"

        # Генерируем уникальный ID для каждого запроса
        self._request_id += 1

        # Формируем JSON-RPC тело запроса
        json_body = {
            "jsonrpc": "2.0",
            "method": endpoint,
            "params": params or {},
            "id": self._request_id
        }

        try:
            session = await self._ensure_session()

            async with session.post(url, json=json_body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"Deribit API error: status={response.status}, "
                        f"body={error_text}"
                    )
                    raise DeribitClientError(
                        f"API returned status {response.status}"
                    )

                json_response = await response.json()

                # Проверяем наличие ошибки в ответе JSON-RPC
                if "error" in json_response:
                    error = json_response["error"]
                    logger.error(
                        f"Deribit JSON-RPC error: code={error.get('code')}, "
                        f"message={error.get('message')}"
                    )
                    raise DeribitClientError(
                        f"JSON-RPC error: {error.get('message')} "
                        f"(code: {error.get('code')})"
                    )

                return json_response.get("result", {})

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise DeribitClientError(f"Network error: {e}")

    async def __aenter__(self) -> "DeribitHttpClient":
        """Контекстный менеджер - вход."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер - выход."""
        await self.close()
