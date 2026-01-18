# Архитектура проекта Crypto Price Tracker

## Общая схема

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Compose                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   FastAPI    │  │  Celery Beat │  │ Celery Worker│               │
│  │   (API)      │  │  (scheduler) │  │  (executor)  │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│         └─────────────────┴─────────────────┘                       │
│                           │                                         │
│                           ▼                                         │
│                 ┌─────────────────┐                                 │
│                 │  Redis (Broker) │                                 │
│                 └────────┬────────┘                                 │
│                          │                                          │
│         ┌────────────────┴────────────────┐                         │
│         ▼                                  ▼                        │
│  ┌──────────────┐                 ┌──────────────┐                  │
│  │   PostgreSQL │                 │ Deribit API  │                  │
│  │   (storage)  │                 │   (source)   │                  │
│  └──────────────┘                 └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Компоненты

### 1. FastAPI Application
- **Порт:** 8000
- **Назначение:** REST API для получения данных о ценах
- **Документация:** `/docs` (Swagger UI) и `/redoc` (ReDoc)
- **Особенности:**
  - Асинхронная работа с БД (SQLAlchemy + asyncpg)
  - Middleware для обработки исключений
  - CORS для кросс-доменных запросов

### 2. Celery Beat
- **Назначение:** Планировщик задач
- **Расписание:** Каждую минуту (`FETCH_INTERVAL: 60.0`)
- **Задача:** `tasks.price_fetcher.fetch_crypto_prices`

### 3. Celery Worker
- **Назначение:** Исполнитель фоновых задач
- **Брокер:** Redis
- **Результаты:** Redis backend

### 4. PostgreSQL
- **Порт:** 5432
- **База:** `crypto_prices`
- **Таблица:** `price_records`
- **Миграции:** Alembic

### 5. Redis
- **Порт:** 6379
- **Назначение:** Брокер сообщений Celery и кэш

### 6. Deribit API
- **API Base URL:** `https://www.deribit.com/api/v2/public`
- **Метод:** `GET /get_index_price?coin={coin}`
- **Тикеры:** `btc_usd`, `eth_usd`

## Структура проекта

```
crypto_price_tracker/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Точка входа FastAPI
│   ├── app.py                     # Инициализация FastAPI
│   ├── api/
│   │   ├── __init__.py            # API router
│   │   └── routes.py              # Эндпоинты (150 строк)
│   ├── clients/
│   │   └── deribit_client.py      # Клиент Deribit (200 строк)
│   ├── config/
│   │   ├── __init__.py            # Фабрика настроек
│   │   ├── base.py                # Базовый класс
│   │   ├── settings.py            # Объединение конфигов
│   │   ├── app.py                 # Настройки FastAPI
│   │   ├── database.py            # Настройки БД
│   │   ├── celery.py              # Настройки Celery
│   │   ├── deribit.py             # Настройки Deribit
│   │   ├── redis.py               # Настройки Redis
│   │   ├── logging.py             # Настройки логирования
│   │   └── monitoring.py          # Настройки мониторинга
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py            # Менеджер подключений
│   │   ├── dependencies.py        # FastAPI dependencies
│   │   └── uow.py                 # Unit of Work паттерн
│   ├── models/
│   │   └── models.py              # SQLAlchemy модели (50 строк)
│   ├── repositories/
│   │   └── price_repository.py    # CRUD операции (120 строк)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py                # Базовые схемы
│   │   ├── requests.py            # Валидация запросов
│   │   └── responses.py           # Формат ответов
│   ├── services/
│   │   └── price_service.py       # Business Logic (100 строк)
│   ├── tasks/
│   │   └── price_fetcher.py       # Celery задача (80 строк)
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── exception_handler.py   # Обработка ошибок
│   │   └── business.py            # Бизнес-логирование
│   └── exceptions/
│       └── exceptions.py          # Кастомные исключения
├── clients/
│   └── deribit_client.py          # Клиент Deribit (отдельный модуль)
├── src/celery_app.py              # Инициализация Celery
├── alembic/
│   ├── versions/                  # Миграции БД
│   └── env.py
├── tests/                         # Тесты
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docs/
│   ├── .env.example
│   ├── ARCHITECTURE.md            # Этот файл
│   └── TECHNICAL_DOCS.md
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Потоки данных

### Поток 1: Сбор цен (Celery)
```
Celery Beat → fetch_crypto_prices → Deribit API → PostgreSQL
```

### Поток 2: Запрос цен (API)
```
Client → FastAPI → PriceService → PriceRepository → PostgreSQL
```

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| API Framework | FastAPI 0.128.0 |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Async Driver | asyncpg 0.31.0 |
| Task Queue | Celery 5.4.0 |
| Message Broker | Redis 5.2.1 |
| HTTP Client | aiohttp 3.13.3 |
| Validation | Pydantic 2.12.5 |
| Configuration | pydantic-settings 2.12.0 |
| Migrations | Alembic 1.18.1 |
| Testing | pytest 9.0.2 |

## Конфигурация

Все настройки загружаются из переменных окружения через `pydantic-settings`.

### Группы настроек

1. **app** — FastAPI (HOST, PORT, DEBUG)
2. **database** — PostgreSQL (HOST, PORT, USER, PASSWORD, NAME)
3. **celery** — Celery (BROKER_URL, RESULT_BACKEND, FETCH_INTERVAL)
4. **deribit** — Deribit API (BASE_URL, TIMEOUT)
5. **redis** — Redis (HOST, PORT, DB)
6. **logging** — Логирование (LEVEL, FORMAT)
7. **monitoring** — Мониторинг (DEBUG, ENABLE_EXCEPTION_LOGGING)

См. также: [Конфигурация](docs/4_CONFIGURATION.md)