# Используем slim-образ с последней стабильной версией Python
FROM python:3.12-slim

# Рабочая директория
WORKDIR /app

# Копируем только requirements.txt для эффективного кеширования
COPY requirements.txt .

# Устанавливаем зависимости в отдельном слое
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
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

# Запуск от непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Команда запуска
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]