
set -e

echo "Applying database migrations..."


# Применяем миграции Alembic
alembic upgrade head

echo "Migrations applied!"

# Запускаем основное приложение
exec "$@"