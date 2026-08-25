from pathlib import Path

from celery import Celery
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import worker.celeryconfig as celeryconfig

celery_app = Celery("worker", config_source=celeryconfig)
# celery -A worker.celery_app 기본 탐색 이름
app = celery_app
