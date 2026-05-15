from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pdfintoword",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.queue.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_routes={
        "app.queue.tasks.convert_pdf_task": {"queue": "default"},
    },
    beat_schedule={
        "expire-jobs-hourly": {
            "task": "app.queue.tasks.expire_jobs_task",
            "schedule": crontab(minute=0),
        },
    },
)
