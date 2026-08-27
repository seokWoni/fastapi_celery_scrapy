# pipeline 공통 사항

from typing import Any

from worker.db import Database


class BasePipeline:
    """모든 pipeline의 부모 클래스.

    open_spider에서 DB 연결과 수집 컨텍스트를 준비하고,
    close_spider에서 잔여 buffer를 flush한 뒤 연결을 정리한다.
    """

    def __init__(self):
        self.db = Database()
        self.buffer: list[dict[str, Any]] = []
        self.customer_id: str | None = None
        self.mall_id: str | None = None
        self.user_id: str | None = None
        self.task_type: str | None = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider) -> None:
        # spider가 이미 Database를 들고 있으면 같은 인스턴스를 공유한다
        if getattr(spider, "db", None) is not None:
            self.db = spider.db

        self.customer_id = getattr(spider, "customer_id", None)
        self.mall_id = getattr(spider, "mall_id", None)
        self.user_id = getattr(spider, "user_id", None)
        self.task_type = getattr(spider, "task_type", None)

        self.db.connect()
        spider.logger.info(
            "%s open_spider: mall_id=%s user_id=%s", type(self).__name__, self.mall_id, self.user_id
        )

    def close_spider(self, spider) -> None:
        try:
            self.flush(spider)
        finally:
            self.db.close()
            spider.logger.info(
                "%s close_spider: items=%s", type(self).__name__, getattr(spider, "item_count", 0)
            )

    def process_item(self, item, spider):
        return item

    def flush(self, spider) -> None:
        """buffer에 쌓인 항목을 저장한다. 저장이 필요한 pipeline에서 구현한다."""
        self.buffer.clear()
