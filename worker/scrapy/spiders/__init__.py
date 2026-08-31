# spider 공통 사항

import importlib
import inspect
from typing import Any

import scrapy

from worker.db import Database

class BaseSpider(scrapy.Spider):
    """모든 mall spider의 부모 클래스.

    하위 spider는 name과 custom_settings(파이프라인 등)만 재정의하고,
    start_requests / parse는 사이트 상황에 맞춰 구현한다.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 요청 공통 정보
        self.customer_id: str | None = kwargs.get("customer_id")
        self.customer_name: str | None = kwargs.get("customer_name")
        self.task_type: str | None = kwargs.get("task_type")

        # 계정 단위 파라미터
        spider_param: dict[str, Any] = kwargs.get("spider_param") or {}
        self.spider_param = spider_param
        self.mall_id: str | None = spider_param.get("mall_id")
        self.user_id: str | None = spider_param.get("user_id")

        # 공통 리소스
        self.db = Database()

        # 수집 통계
        self.item_count = 0

        self.logger.info(
            "spider init: name=%s task_type=%s mall_id=%s user_id=%s period=%s~%s",
            self.name,
            self.task_type,
            self.mall_id,
            self.user_id,
            self.start_date,
            self.end_date,
        )

    def start_requests(self):
        raise NotImplementedError(f"{type(self).__name__}.start_requests must be implemented")