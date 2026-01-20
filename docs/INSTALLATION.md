# Руководство по установке


## Требования

- Docker
- Docker Compose

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/lamauspex/Test_Task
```
```bash
cd crypto_price_tracker
```

### 2. Запуск Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down
```

### 3. Проверка работоспособности

```bash
# Статус контейнеров
docker-compose ps


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
