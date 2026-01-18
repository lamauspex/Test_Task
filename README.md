# crypto-price-tracker

Приложение для отслеживания криптовалютных цен, которое получает курсы BTC и ETH с биржи Deribit и предоставляет REST API.

## Функциональность

- Получает индексные цены BTC/USD и ETH/USD с API Deribit каждую минуту
- Сохраняет цены в базу данных PostgreSQL
- REST API для получения данных о ценах с фильтрацией
- Асинхронный клиент с использованием aiohttp
- Celery + Redis для периодических задач

## Стек технологий

- **Бэкенд:** FastAPI, Python 3.12+
- **База данных:** PostgreSQL
- **Очередь задач:** Celery + Redis (брокер сообщений)
- **HTTP клиент:** aiohttp (асинхронный)
- **ORM:** SQLAlchemy 2.0
- **Контейнеризация:** Docker, Docker Compose

## Быстрый старт

### Требования

- Docker & Docker Compose v2
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитории>
cd crypto-price-tracker
```

2. Запустите все сервисы:
```bash
docker-compose up -d
```

3. Проверьте статус сервисов:
```bash
docker-compose ps
```

4. Проверьте логи Celery:
```bash
docker-compose logs celery-worker
docker-compose logs celery-beat
```

### Доступ к сервисам

| Сервис | URL | Описание |
|--------|-----|----------|
| API | http://localhost:8000 | REST API |
| Swagger Docs | http://localhost:8000/docs | Интерактивная документация |
| Redis | localhost:6379 | Брокер Celery |
| PostgreSQL | localhost:5432 | База данных |

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

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Redis     │  │  PostgreSQL │  │    App      │              │
│  │  (Broker)   │  │     (DB)    │  │  (FastAPI)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                │                  │                    │
│         └────────────────┼──────────────────┘                    │
│                          │                                       │
│              ┌───────────┴───────────┐                          │
│              │      Celery Beat      │  (планировщик задач)     │
│              └───────────┬───────────┘                          │
│                          │                                       │
│              ┌───────────┴───────────┐                          │
│              │    Celery Worker      │  (исполнитель задач)     │
│              └───────────────────────┘                          │
│                                                                 │
│  Внешний API: Deribit (https://www.deribit.com/api/v2/public)  │
└─────────────────────────────────────────────────────────────────┘
```

## Решения в архитектуре (Design Decisions)

### 1. Почему Redis для Celery?

**Проблема:** Celery требует брокера сообщений для передачи задач между beat (планировщиком) и worker (исполнителем).

**Варианты и причины выбора:**

| Брокер | Плюсы | Минусы |
|--------|-------|--------|
| **Redis** ✅ | • In-memory → сверхбыстрый<br>• Простая настройка<br>• Поддержка результатов | Требует отдельный контейнер |
| RabbitMQ | • Промышленный стандарт<br>• Надёжность | • Сложнее в настройке<br>• Больше ресурсов |
| PostgreSQL | • Уже есть в стеке | • Нагрузка на БД<br>• Медленнее очереди |

**Вывод:** Redis — оптимальный выбор для тестового задания:
- Быстрый (in-memory)
- Простая интеграция с Celery
- Минимальные ресурсы

### 2. Почему aiohttp вместо requests?

```python
# Синхронный (блокирующий)
import requests
response = requests.get(url)  # Ждём ответа, блокируем поток

# Асинхронный (неблокирующий)
import aiohttp
async with session.get(url) as response:  # Можно делать другие задачи
    data = await response.json()
```

**Преимущества для нашей задачи:**
- Одновременные запросы к API Deribit для BTC и ETH
- Не блокирует FastAPI во время ожидания ответа внешнего API
- Меньше потребление ресурсов при высокой нагрузке

### 3. Clean Architecture

Проект разделён на слои с чёткой ответственностью:

```
┌─────────────────────────────────────────────────────┐
│                    API Layer                         │
│              (routes.py, schemas.py)                 │
├─────────────────────────────────────────────────────┤
│                 Service Layer                        │
│               (price_service.py)                     │
├─────────────────────────────────────────────────────┤
│                Repository Layer                      │
│             (price_repository.py)                    │
├─────────────────────────────────────────────────────┤
│                   Data Layer                         │
│              (models.py, database.py)                │
├─────────────────────────────────────────────────────┤
│                 External API                         │
│              (deribit_client.py)                     │
└─────────────────────────────────────────────────────┘
```

**Почему это важно:**
- Тестируемость: каждый слой можно мокать
- Заменимость: легко сменить БД или внешний API
- Чистота кода: каждая часть делает одну вещь

### 4. Почему не глобальные переменные?

Глобальные переменные — антипаттерн в production-коде:

| Проблема | Решение |
|----------|---------|
| Сложно тестировать | Dependency Injection |
| Гонки данных в async | Передача зависимостей |
| Жёсткая связность | Интерфейсы и абстракции |

**Наш подход:**
```python
# ❌ Плохо: глобальная переменная
db = Database()

# ✅ Хорошо: dependency injection
async def get_prices(repo: PriceRepository = Depends(get_repo)):
    return await repo.get_all()
```

### 5. Почему Pydantic?

- **Валидация на входе:** автоматическая проверка типов
- **Сериализация:** преобразование в JSON
- **Type safety:** IDE подсказывает ошибки до запуска
- **Документация:** схемы → Swagger UI

### 6. Celery Beat + Worker

Для периодических задач используются два компонента:

| Компонент | Роль |
|-----------|------|
| **Celery Beat** | Планировщик — запускает задачи по расписанию (каждую минуту) |
| **Celery Worker** | Исполнитель — выполняет задачи (получает цены, сохраняет в БД) |

```python
# beat_schedule в celery.py
beat_schedule = {
    "fetch-crypto-prices-every-minute": {
        "task": "src.tasks.price_fetcher.fetch_crypto_prices",
        "schedule": 60.0,  # каждую минуту
    },
}
```

### 7. Почему PostgreSQL?

- **ACID:** гарантия целостности данных о ценах
- **DECIMAL:** точные финансовые расчёты без float-погрешностей
- **Индексы:** быстрые запросы по timestamp и ticker
- **JSONB:** возможность расширения для дополнительных данных

## Структура проекта

```
crypto-price-tracker/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Точка входа FastAPI
│   ├── config/
│   │   ├── base.py             # Базовые классы конфигурации
│   │   ├── settings.py         # Централизованные настройки
│   │   ├── app.py              # Настройки приложения
│   │   ├── database.py         # Конфигурация PostgreSQL
│   │   ├── celery.py           # Конфигурация Celery + Redis
│   │   ├── deribit.py          # Конфигурация Deribit API
│   │   └── redis.py            # Конфигурация Redis
│   ├── database/
│   │   ├── database.py         # Менеджер подключений
│   │   └── dependencies.py     # Зависимости FastAPI
│   ├── api/
│   │   └── routes.py           # API эндпоинты
│   ├── services/
│   │   └── price_service.py    # Бизнес-логика
│   ├── repositories/
│   │   └── price_repository.py # Работа с БД
│   ├── clients/
│   │   └── deribit_client.py   # Клиент Deribit (aiohttp)
│   ├── schemas/
│   │   ├── requests.py         # Pydantic схемы запросов
│   │   └── responses.py        # Pydantic схемы ответов
│   ├── models/
│   │   └── models.py           # SQLAlchemy модели
│   ├── tasks/
│   │   └── price_fetcher.py    # Celery задачи
│   └── exceptions/
│       └── exceptions.py       # Кастомные исключения
├── clients/
│   └── deribit_client.py       # Клиент Deribit (для использования вне DI)
├── tests/                       # Unit тесты
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Тестирование

```bash
# Запуск тестов
docker-compose exec app pytest tests/ -v

# Запуск с покрытием
docker-compose exec app pytest tests/ --cov=src --cov=clients
```

## Остановка

```bash
docker-compose down
```

## Лицензия

MIT License
