import os
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv(Path(__file__).resolve().parent / ".env")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "celery_scrapy")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def build_dsn() -> str:
    user = quote_plus(DB_USER)
    password = quote_plus(DB_PASSWORD)
    return f"mysql+pymysql://{user}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"


class Database:
    """spider / pipeline이 공유하는 DB 접근 헬퍼."""

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or build_dsn()
        self._engine: Engine | None = None

    def connect(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self.dsn,
                pool_pre_ping=True,
                pool_recycle=3600,
                future=True,
            )
        return self._engine

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def fetch_all(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self.connect().connect() as conn:
            rows = conn.execute(text(query), params or {}).mappings().all()
        return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def execute(self, query: str, params: dict[str, Any] | list[dict[str, Any]] | None = None) -> int:
        with self.connect().begin() as conn:
            result = conn.execute(text(query), params or {})
        return result.rowcount
