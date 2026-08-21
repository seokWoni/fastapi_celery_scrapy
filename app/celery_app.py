import os
import env
from celery import Celery

celery_app = Celery(
    "scraper",
    broker=env.BROKER_URL,
    backend=env.get_result_backend(),
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_extended=True,
)
