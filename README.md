# crypto-price-tracker

Приложение для отслеживания криптовалютных цен, которое получает курсы BTC и ETH с биржи Deribit и предоставляет REST API.

## Функциональность

- Получает индексные цены BTC/USD и ETH/USD с API Deribit каждую минуту
- Сохраняет цены в базу данных PostgreSQL
- REST API для получения данных о ценах с фильтрацией
- Асинхронный клиент с использованием aiohttp
- Celery для периодических задач

## Стек технологий

- **Бэкенд:** FastAPI, Python 3.11+
- **База данных:** PostgreSQL
- **Очередь задач:** Celery + Redis (брокер)
- **HTTP клиент:** aiohttp
- **ORM:** SQLAlchemy
- **Контейнеризация:** Docker, Docker Compose

## Быстрый старт

### Требования

- Docker & Docker Compose
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd crypto-price-tracker
```

2. Создайте файл окружения:
```bash
cp .env.example .env
```

3. Запустите приложение:
```bash
docker-compose up -d
```

4. Доступ к приложению:
   - API: http://localhost:8000
   - Документация API: http://localhost:8000/docs

## API эндпоинты

### Получить все цены по тикеру
```http
GET /api/v1/prices?ticker={btc_usd|eth_usd}
```

### Получить последнюю цену по тикеру
```http
GET /api/v1/prices/latest?ticker={btc_usd|eth_usd}
```

### Получить цены по диапазону дат
```http
GET /api/v1/prices/date-range?ticker={btc_usd|eth_usd}&start_date=1704067200&end_date=1704153600
```

## Решения в архитектуре (Design Decisions)

### 1. Архитектура

Проект следует принципам **Clean Architecture** с чётким разделением ответственности:

- **app/** - слой приложения FastAPI (контроллеры, маршруты, схемы)
- **clients/** - клиенты внешних API (клиент Deribit)
- **tasks/** - задачи Celery для фоновых заданий
- **services/** - слой бизнес-логики

### 2. Проектирование базы данных

Использование PostgreSQL с ORM SQLAlchemy:

```sql
CREATE TABLE price_records (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ticker (ticker),
    INDEX idx_timestamp (timestamp)
);
```

**Почему PostgreSQL?**
- Надёжная реляционная база данных с отличной производительностью
- Нативная поддержка больших чисел (DECIMAL для цен)
- Оптимизация индексов для запросов по временным меткам

### 3. Асинхронный дизайн

- **aiohttp** для неблокирующих HTTP-запросов к API Deribit
- **asyncpg** для асинхронных операций с базой данных
- **Асинхронный SQLAlchemy** для ORM операций

Это обеспечивает высокую производительность при одновременном получении и сохранении данных.

### 4. Celery для периодических задач

Celery используется для периодического получения цен, так как:
- Надёжная очередь задач с персистентностью
- Встроенный планировщик (celery beat)
- Лёгкое масштабирование между воркерами
- Интеграция с Redis в качестве брокера

### 5. Почему не глобальные переменные?

Глобальные переменные не используются, потому что:
- Тестируемость: сложно мокать в юнит-тестах
- Проблемы конкурентности: состояния гонки в асинхронном коде
- Управление конфигурацией: переменные окружения более гибкие
- Clean Architecture: зависимости должны быть внедрены

### 6. Pydantic для валидации

Использование схем Pydantic для:
- Валидация запросов
- Сериализация ответов
- Безопасность типов

### 7. Стратегия Docker

Конфигурация из двух контейнеров:
1. **app** - FastAPI приложение
2. **postgres** - База данных PostgreSQL (используется как брокер для Celery)

Все сервисы связаны через общую сеть `crypto-network`.

## Структура проекта

```
crypto-price-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Точка входа FastAPI приложения
│   ├── config/                 # Конфигурация
│   │   ├── __init__.py
│   │   ├── base.py             # Базовые классы конфигурации
│   │   ├── settings.py         # Настройки приложения
│   │   ├── app.py              # Настройки приложения
│   │   ├── database.py         # Конфигурация БД
│   │   ├── celery.py           # Конфигурация Celery
│   │   ├── deribit.py          # Конфигурация Deribit API
│   │   └── monitoring.py       # Конфигурация мониторинга
│   ├── database/               # Работа с БД
│   │   ├── __init__.py
│   │   ├── database.py         # Менеджер подключений
│   │   └── dependencies.py     # Зависимости FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API эндпоинты
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   └── price_service.py
│   ├── repositories/           # Репозитории
│   │   ├── __init__.py
│   │   └── price_repository.py
│   ├── clients/                # Клиенты внешних API
│   │   ├── __init__.py
│   │   └── deribit_client.py
│   ├── schemas/                # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── requests.py
│   │   └── responses.py
│   ├── models/                 # Модели SQLAlchemy
│   │   ├── __init__.py
│   │   ├── models_base.py
│   │   ├── models.py
│   │   ├── mixin/
│   │   └── decorators/
│   ├── middleware/             # Middleware
│   │   ├── __init__.py
│   │   └── exception_handler.py
│   └── tasks/                  # Celery задачи
│       ├── __init__.py
│       ├── celery.py
│       └── price_fetcher.py
├── Docker/
│   ├── Dockerfile
│   └── Docker/
│       └── entrypoint.sh
├── docker-compose.yml
├── requirements.txt
├── .env
└── .env.example
```

## Тестирование

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ --cov=app --cov=clients --cov=tasks
```

## Лицензия

MIT License
