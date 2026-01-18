# Crypto Price Tracker

Приложение для отслеживания криптовалютных цен (BTC/USD, ETH/USD) с биржи Deribit.

## 🟢 Быстрый старт

```bash
git clone https://github.com/lamauspex/Test_Task/blob/master/Dockerfile
docker-compose up -d
```

## 🟢 Сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| API | http://localhost:8000 | REST API |
| Swagger Docs | http://localhost:8000/docs | Интерактивная документация |
| PostgreSQL | localhost:5432 | База данных |
| Redis | localhost:6379 | Брокер Celery |

## 🟢 API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/prices/all?ticker=btc_usd` | Все цены тикера |
| GET | `/api/v1/prices/latest?ticker=btc_usd` | Последняя цена |
| GET | `/api/v1/prices/date-range?ticker=btc_usd&start_date=1704067200&end_date=1704153600` | Цены по диапазону |

## 🟢 Документация

- [Установка](docs/INSTALLATION.md) — развёртывание проекта
- [Архитектура](docs/ARCHITECTURE.md) — общая схема и компоненты
- [Техническая документация](docs/TECHNICAL_DOCS.md) — детали реализации



## Контакты
Если у вас есть вопросы или предложения, не стесняйтесь связаться со мной:

- Имя: Резник Кирилл
- Email: lamauspex@yandex.ru
- GitHub: https://github.com/lamauspex
- Telegram: @lamauspex