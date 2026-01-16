""" Периодические задачи Celery для получения цен криптовалют """

from app.config.celery import celery_app
from app.services.price_service import PriceService


@celery_app.task(bind=True)
def fetch_crypto_prices(self):
    """Получить текущие цены криптовалют с Deribit"""
    self.update_state(state="PROGRESS", meta={"status": "Fetching prices..."})
    service = PriceService()
    prices = service.fetch_all_prices()
    return {"status": "success", "count": len(prices)}


@celery_app.task(bind=True)
def sync_prices_to_database(self):
    """Синхронизировать цены в базу данных"""
    self.update_state(state="PROGRESS", meta={
                      "status": "Syncing to database..."})
    service = PriceService()
    count = service.sync_prices_to_db()
    return {"status": "success", "synced": count}
