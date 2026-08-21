from pathlib import Path
from urllib.parse import quote_plus
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

BROKER_URL = os.getenv("BROKER_URL")
RESULT_BACKEND = os.getenv("RESULT_BACKEND")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")


def get_result_backend() -> str:
    if RESULT_BACKEND:
        return RESULT_BACKEND
    user = quote_plus(DB_USER or "")
    password = quote_plus(DB_PASSWORD or "")
    return f"db+mysql+pymysql://{user}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
