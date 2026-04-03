from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "price_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.timezone = "UTC"



# Периодическая задача
celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.services.tasks.fetch_prices.fetch_prices",
        "schedule": 60.0,
    },
}
