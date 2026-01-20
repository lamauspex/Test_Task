"""Базовые типы для приложения."""

from typing import Literal


# Валидные тикеры как Literal типы (верхний регистр)
BTC_USD = Literal["BTC_USD"]
ETH_USD = Literal["ETH_USD"]
TickerStr = BTC_USD | ETH_USD

# Список всех валидных тикеров для проверки (верхний регистр)
VALID_TICKERS = ["BTC_USD", "ETH_USD"]
