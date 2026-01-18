"""
Сервис цен для бизнес-логики операций
Работает с UnitOfWork для транзакционности
"""

from typing import List

from src.database.uow import UnitOfWork
from src.exceptions.exceptions import PriceNotFoundError
from src.middleware.business import get_business_logger
from src.schemas import PriceRecordResponse
from clients import DeribitClient, PriceData


class PriceService:
    """ Сервис для операций с ценами """

    def __init__(
        self,
        deribit_client: DeribitClient | None = None,
    ) -> None:
        """ Инициализация сервиса цен """

        self._deribit_client = deribit_client or DeribitClient()
        self._business_logger = get_business_logger()

    @property
    def deribit_client(self) -> DeribitClient:
        """ Получить клиент Deribit """

        return self._deribit_client

    async def save_price_data(
        self,
        uow: UnitOfWork,
        price_data: PriceData,
    ) -> None:
        """ Сохранить данные о цене через репозиторий """
        record = await uow.prices.save_price_data(
            ticker=price_data.ticker,
            price=price_data.price,
            timestamp=price_data.timestamp
        )

        self._business_logger.log_price_saved(
            ticker=record.ticker,
            price=record.price,
            timestamp=record.timestamp
        )

    async def fetch_and_save_all_prices(
        self,
        uow: UnitOfWork,
    ) -> List[str]:
        """
        Получить все цены с Deribit и сохранить в базу данных

        Вся операция выполняется в рамках одной транзакции (uow)
        """
        price_data_map = await self._deribit_client.fetch_all_prices()
        saved_tickers = []

        for ticker, price_data in price_data_map.items():
            await uow.prices.save_price_data(
                ticker=price_data.ticker,
                price=price_data.price,
                timestamp=price_data.timestamp
            )
            saved_tickers.append(ticker)

        self._business_logger.log_prices_saved(saved_tickers)

        return saved_tickers

    async def get_prices_by_ticker(
        self,
        uow: UnitOfWork,
        ticker: str,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[PriceRecordResponse]:
        """
        Получить записи о ценах для тикера через репозиторий
        """
        return await uow.prices.get_prices_by_ticker(
            ticker=ticker,
            limit=limit,
            offset=offset
        )

    async def get_latest_price(
        self,
        uow: UnitOfWork,
        ticker: str,
    ) -> PriceRecordResponse:
        """
        Получить последнюю цену для тикера через репозиторий

        """
        record = await uow.prices.get_latest_price(ticker)

        if not record:
            raise PriceNotFoundError(ticker)

        return PriceRecordResponse.model_validate(record)

    async def get_prices_by_date_range(
        self,
        uow: UnitOfWork,
        ticker: str,
        start_date: int,
        end_date: int,
        limit: int = 1000,
    ) -> List[PriceRecordResponse]:
        """
        Получить записи о ценах для тикера в диапазоне дат
        """
        return await uow.prices.get_prices_by_date_range(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )


def get_price_service() -> PriceService:
    """
    Фабрика для получения инстанса сервиса цен
    """
    return PriceService()
