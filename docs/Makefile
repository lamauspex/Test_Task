# ============================================
# Crypto Tracker - команды управления
# ============================================
docker-compose up -d --build

# Пересобери и перезапусти
docker-compose build app
# Запуск всех сервисов
docker-compose up -d

# Зайди в контейнер
docker-compose exec app bash

# Создай новую миграцию
alembic revision --autogenerate -m "Initial migration"

# Примени её
alembic upgrade head

# Выйди
exit

# Перезапусти контейнер
docker-compose restart app


# Остановка всех сервисов
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