from typing import Any

import scrapy
from app.celery_app import celery_app
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals

@celery_app.task(bind=True)
def do_spider(self, payload: dict[str, Any]):
    spider_name = payload.get("spider_name") or payload.get("task_type")
    spider_args = payload.get("spider_args", payload)
    spider_cls = SPIDERS.get(spider_name)
    if spider_cls is None:
        raise ValueError(f"unknown spider: {spider_name}")
    items: list[dict[str, Any]] = []

    def collect_item(item, response, spider):
        items.append(dict(item))

    settings = get_project_settings()
    settings.set("LOG_ENABLED", True)

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(spider_cls)
    crawler.signals.connect(collect_item, signal=signals.item_scraped)
    process.crawl(crawler, **spider_args)
    process.start()  # 크롤이 끝날 때까지 블로킹

