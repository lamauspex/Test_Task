# Используем slim-образ с последней стабильной версией Python
FROM python:3.12-slim

# Устанавливаем postgresql-client для pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app/src

# Копируем только необходимые файлы для установки зависимостей
COPY pyproject.toml .
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Устанавливаем зависимости из pyproject.toml
RUN pip install .

# Копируем исходный код (после установки зависимостей, для использования кэша слоёв)
COPY src/ ./
COPY clients/ ../clients/
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/entrypoint_celery.sh /usr/local/bin/entrypoint_celery.sh
RUN chmod +x /usr/local/bin/entrypoint_celery.sh

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Порт для FastAPI
EXPOSE 8000

# Создаём пользователя (без chown -R, т.к. используем volume mount)
RUN useradd --create-home --shell /bin/bash appuser

USER appuser

# Команда запуска
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
