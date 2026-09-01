# spider 공통 사항

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

        self.customer_id: str | None = kwargs.get("customer_id")
        self.customer_name: str | None = kwargs.get("customer_name")
        self.task_type: str | None = kwargs.get("task_type")

        period: dict[str, Any] = kwargs.get("period") or {}
        self.start_date: str | None = period.get("start_date")
        self.end_date: str | None = period.get("end_date")

        spider_param: dict[str, Any] = kwargs.get("spider_param") or {}
        self.spider_param = spider_param
        self.mall_id: str | None = spider_param.get("mall_id")
        self.user_id: str | None = spider_param.get("user_id")
        self.goods_list: list[dict[str, Any]] = spider_param.get("goods_list") or []

        self.db = Database()
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

    @property
    def goods_ids(self) -> list[str]:
        return [goods["goods_id"] for goods in self.goods_list if "goods_id" in goods]

    def build_meta(self, **extra: Any) -> dict[str, Any]:
        meta = {
            "customer_id": self.customer_id,
            "mall_id": self.mall_id,
            "user_id": self.user_id,
            "task_type": self.task_type,
        }
        meta.update(extra)
        return meta

    async def start(self):
        """Scrapy 2.13+는 start_requests() 대신 start()를 호출한다."""
        for request in self.start_requests():
            yield request

    def start_requests(self):
        raise NotImplementedError(f"{type(self).__name__}.start_requests must be implemented")

    def parse(self, response):
        raise NotImplementedError(f"{type(self).__name__}.parse must be implemented")
