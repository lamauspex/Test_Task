crypto_price_tracker/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI приложение
│   ├── config.py               # Конфигурация (без глобальных переменных)
│   ├── database.py             # Подключение к PostgreSQL
│   ├── models.py               # SQLAlchemy модели
│   ├── schemas.py              # Pydantic схемы
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API эндпоинты
│   └── services/
│       ├── __init__.py
│       └── price_service.py    # Бизнес-логика
├── clients/
│   ├── __init__.py
│   └── deribit_client.py       # aiohttp клиент Deribit
├── tasks/
│   ├── __init__.py
│   └── price_fetcher.py        # Celery задачи
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_client.py
├── celerybeat-schedule
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md