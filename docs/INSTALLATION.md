# Руководство по установке


## 🟢 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/lamauspex/Test_Task/blob/master/Dockerfile
```


### 2. Запуск с помощью Docker Compose

```bash
# Запуск всех сервисов в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down
```

### 4. Проверка работоспособности

После запуска выполните:

```bash
# Проверка статуса контейнеров
docker-compose ps

# Тест API
curl http://localhost:8000/api/v1/prices?ticker=btc_usd

# Проверка Swagger документации
open http://localhost:8000/docs
```

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

## 🟢 Docker Compose сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| app | 8000 | FastAPI приложение |
| postgres | 5432 | PostgreSQL база данных |
| redis | 6379 | Redis брокер сообщений |

## 🟢 Устранение неполадок

### Ошибка подключения к PostgreSQL

```bash
# Проверьте, что контейнер запущен
docker-compose ps

# Проверьте логи
docker-compose logs postgres
```

### Ошибка подключения к Redis

```bash
# Проверьте логи Redis
docker-compose logs redis
```

### Celery задачи не выполняются

```bash
# Проверьте логи worker
docker-compose logs worker

# Убедитесь, что redis запущен
docker-compose logs redis
```

См. также: [Частые проблемы](docs/9_TROUBLESHOOTING.md)