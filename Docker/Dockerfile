# Используем slim-образ с последней стабильной версией Python
FROM python:3.12-slim

# Устанавливаем postgresql-client для pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Копируем entrypoint скрипт
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

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
ENTRYPOINT ["/entrypoint.sh"]
