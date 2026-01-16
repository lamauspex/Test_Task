# ============================================
# Crypto Tracker - команды управления
# ============================================

# Запуск всех сервисов
up:
	docker-compose up -d

# Остановка всех сервисов
down:
	docker-compose down

# Перезапуск всех сервисов
restart: down up

# Просмотр логов
logs:
	docker-compose logs -f app

# Логи базы данных
logs-db:
	docker-compose logs -f postgres

# Полная пересборка и запуск
rebuild:
	docker-compose build --no-cache
	docker-compose up -d

# Остановка и удаление данных БД
clean:
	docker-compose down -v

# Статус контейнеров
status:
	docker-compose ps

# Подключение к контейнеру приложения
shell:
	docker-compose exec app bash

# Подключение к базе данных
db:
	docker-compose exec postgres psql -U postgres -d crypto_prices