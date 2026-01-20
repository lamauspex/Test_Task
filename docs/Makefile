# ============================================
# Crypto Tracker - команды управления
# ============================================

# Запуск всех сервисов
up:
	docker-compose up -d

# Пересборка и запуск
rebuild:
	docker-compose build --no-cache
	docker-compose up -d

# Перезапуск конкретного сервиса
restart-%:
	docker-compose restart $*

# Остановка всех сервисов
down:
	docker-compose down

# Остановка и удаление данных БД
clean:
	docker-compose down -v

# Статус контейнеров
ps:
	docker-compose ps

# ============================================
# Логи
# ============================================
logs-%:
	docker-compose logs -f $*

logs:       logs-% app
logs-app:   logs-% app
logs-db:    logs-% postgres
logs-redis: logs-% redis
logs-worker:logs-% celery-worker
logs-beat:  logs-% celery-beat

# ============================================
# Shell
# ============================================
shell:
	docker-compose exec app bash

shell-%:
	docker-compose exec $* bash

shell-db:   shell-% postgres
shell-redis:shell-% redis
shell-worker:shell-% celery-worker

# ============================================
# База данных
# ============================================
db:
	docker-compose exec postgres psql -U postgres -d crypto_prices

migrate:
	docker-compose exec app alembic -c /app/alembic.ini upgrade head

migration:
	docker-compose exec app alembic revision --autogenerate -m "$(msg)"

# ============================================
# Тесты
# ============================================
test:
	docker-compose exec app pytest

test-%:
	docker-compose exec app pytest -k "$*"