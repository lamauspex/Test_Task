# Руководство по установке

## Требования

- Docker
- Docker Compose

## Установка

### 1. Клонирование репозитория

```bash
git clone https://gitlab.com/username/crypto_price_tracker.git
cd crypto_price_tracker
```

### 2. Запуск Docker Compose

```bash
# Сборка и запуск всех сервисов в фоновом режиме
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down
```

### 3. Проверка работоспособности

```bash
# Статус контейнеров
docker-compose ps

# Тест API
curl http://localhost:8000/api/v1/prices/all?ticker=btc_usd

# Swagger документация
open http://localhost:8000/docs
```

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| app | 8000 | FastAPI приложение |
| postgres | 5432 | PostgreSQL база данных |
| redis | 6379 | Redis брокер сообщений |
| celery-worker | — | Исполнитель задач Celery |
| celery-beat | — | Планировщик задач Celery |

## Устранение неполадок

### Ошибка подключения к PostgreSQL

```bash
docker-compose ps
docker-compose logs postgres
```

### Ошибка подключения к Redis

```bash
docker-compose logs redis
```

### Celery задачи не выполняются

```bash
docker-compose logs worker
docker-compose logs beat
```

См. также: [ARCHITECTURE.md](ARCHITECTURE.md), [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)

## 🟢 Режим разработки

Для разработки без Docker:

### 1. Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
.\venv\Scripts\activate   # Windows
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте PostgreSQL и Redis локально

```bash
# PostgreSQL
sudo systemctl start postgresql
sudo -u postgres createdb crypto_prices

# Redis
sudo systemctl start redis
```

### 4. Запустите миграции

```bash
alembic upgrade head
```

### 5. Запустите компоненты

В разных терминалах:

```bash
# FastAPI (с hot reload)
uvicorn src.main:app --reload

# Celery Worker
celery -A src.celery_app worker -l info

# Celery Beat
celery -A src.celery_app beat -l info
```