from celery import Celery
from app.config import settings

celery_app = Celery(
    "agent_orchestration",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.queue.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)
