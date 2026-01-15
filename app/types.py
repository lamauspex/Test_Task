"""Базовые типы для приложения."""

from typing import Literal


# Валидные тикеры как Literal типы
BTC_USD = Literal["btc_usd"]
ETH_USD = Literal["eth_usd"]
TickerStr = BTC_USD | ETH_USD

# Список всех валидных тикеров для проверки
VALID_TICKERS = ["btc_usd", "eth_usd"]
