from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "price_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url,
)

celery_app.conf.timezone = "UTC"
