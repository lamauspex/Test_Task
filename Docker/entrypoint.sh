#!/bin/bash
set -e

export PYTHONPATH=${PYTHONPATH:-/app}

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}"; do
echo "PostgreSQL is unavailable - sleeping"
sleep 1
done
echo "PostgreSQL is ready!"

echo "Applying database migrations..."
alembic upgrade head
echo "Migrations applied!"

echo "Starting FastAPI application..."
exec "$@"