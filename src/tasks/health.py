""" health_check """

from src.celery_app import celery_app


@celery_app.task(bind=True)
def health_check(self):
    """
    Проверка работоспособности Celery воркера.

    Returns:
        dict: Статус воркера
    """
    return {
        "status": "healthy",
        "worker": self.request.hostname,
        "pid": self.request.pid
    }
