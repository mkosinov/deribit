from celery import Celery
from celery.schedules import crontab

from core.config import settings

celery_app = Celery(
    "price_ticker",
    broker=settings.REDIS_URL,
    include=["tasks.price_tickers"],
)

celery_app.conf.update(
    task_ignore_result=True,
    timezone="UTC",
    beat_schedule={
        "fetch-current-prices-every-minute": {
            "task": "price_tickers.fetch_current_prices",
            "schedule": crontab(minute="*"),
        },
    },
)
