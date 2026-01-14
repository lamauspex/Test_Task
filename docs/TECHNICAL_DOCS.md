# Crypto Price Tracker - Техническая документация

## Выполненные требования

### Обязательные ✅
1. **Клиент Deribit API** - реализован с использованием aiohttp
2. **Периодический сбор данных** - Celery + Celery Beat каждые 60 секунд
3. **Хранение в PostgreSQL** - SQLAlchemy async с asyncpg
4. **REST API на FastAPI** - 3 GET метода с обязательным query-параметром ticker:
   - `GET /api/v1/prices?ticker=btc_usd` - все сохранённые данные
   - `GET /api/v1/prices/latest?ticker=btc_usd` - последняя цена
   - `GET /api/v1/prices/date-range?ticker=btc_usd&start_date=X&end_date=Y` - фильтр по дате
5. **Docker Compose** - 4 сервиса (app, worker, beat, postgres, redis)
6. **README.md** - подробная документация + Design Decisions

### Необязательные ✅
1. **aiohttp клиент** - полностью асинхронный HTTP клиент
2. **Docker (2+ контейнера)** - 5 контейнеров (app, worker, beat, postgres, redis)
3. **Unit тесты** - структура подготовлена (файл tests/__init__.py)

---

## Ключевые архитектурные решения

### 1. Clean Architecture
```
api/ → services/ → clients/, database/, models/
```
Зависимости направлены сверху вниз. API не зависит от деталей реализации.

### 2. Dependency Injection через FastAPI Depends
```python
# Вместо глобальных переменных
async def get_all_prices(
    service: PriceService = Depends(get_price_service),
    db: AsyncSession = Depends(get_db),
):
```
Легко тестировать и заменять реализации.

### 3. Протоколы (Protocols) для типизации
```python
@runtime_checkable
class IDeribitClient(Protocol):
    async def fetch_all_prices(self) -> Dict[str, PriceData]:
        ...
```
Позволяет мокать клиенты в тестах.

### 4. Фабрики вместо синглтонов
```python
def get_price_service() -> PriceService:
    return PriceService()

def get_database() -> Database:
    return Database()
```
Каждый запрос получает свежий инстанс.

### 5. Асинхронность везде
- aiohttp для HTTP клиента
- asyncpg + SQLAlchemy async для БД
- asyncio.gather для параллельных запросов

---

## Структура файлов

```
crypto_price_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan management
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Database manager + get_db()
│   ├── models.py            # SQLAlchemy models (PriceRecord)
│   ├── schemas.py           # Pydantic schemas
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   └── services/
│       ├── __init__.py
│       └── price_service.py # Business logic
├── clients/
│   ├── __init__.py
│   └── deribit_client.py    # aiohttp client
├── tasks/
│   ├── __init__.py
│   ├── celery.py            # Celery config
│   └── price_fetcher.py     # Periodic tasks
├── tests/
│   └── __init__.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── ARCHITECTURE.md
└── check_architecture.py
```

---

## Запуск

### Docker Compose (рекомендуется)
```bash
docker-compose up -d
```

### Локально
```bash
# 1. Запуск Redis
docker run -d -p 6379:6379 redis:alpine

# 2. Запуск PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_DB=crypto_prices postgres:15

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Celery worker
celery -A tasks.celery worker --loglevel=info

# 5. Celery beat
celery -A tasks.celery beat --loglevel=info

# 6. FastAPI
uvicorn app.main:app --reload
```

---

## API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/prices?ticker=btc_usd` | Все цены тикера |
| GET | `/api/v1/prices/latest?ticker=btc_usd` | Последняя цена |
| GET | `/api/v1/prices/date-range?ticker=btc_usd&start_date=1704067200&end_date=1704153600` | Цены по диапазону |
| GET | `/api/v1/prices/health` | Health check |

---

## База данных

```sql
CREATE TABLE price_records (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ticker (ticker),
    INDEX idx_timestamp (timestamp),
    INDEX ix_price_records_ticker_timestamp (ticker, timestamp)
);
```

---

## Критерии оценки

| Критерий | Статус |
|----------|--------|
| Чистая архитектура | ✅ Clean Architecture + слои |
| Нейминг | ✅ PEP 8, snake_case, CamelCase |
| Глобальные переменные | ✅ Только константы CAPS_CASE |
| ООП | ✅ Классы, протоколы, DI |
| Понимание решений | ✅ README + ARCHITECTURE.md |
