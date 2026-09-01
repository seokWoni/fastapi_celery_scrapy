import importlib
import inspect
from copy import deepcopy
from typing import Any

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from worker.celery_app import celery_app
from worker.scrapy.spiders import BaseSpider


def _run_crawl(spider_cls: type[BaseSpider], params: dict[str, Any]) -> None:
    """Celery worker(--pool=solo)에서 CrawlerProcess를 직접 실행한다."""
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_cls, **params)
    process.start()


def get_spider_cls(mall_id: str, task_type: str) -> type[BaseSpider]:
    module_path = f"worker.scrapy.spiders.{mall_id}.{task_type}"

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise ValueError(f"spider module not found: {module_path}") from exc

    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseSpider) and obj is not BaseSpider and obj.__module__ == module_path:
            return obj

    raise ValueError(f"BaseSpider subclass not found in {module_path}")


@celery_app.task(bind=True)
def do_spider(self, payload: dict[str, Any]):
    task_type = payload.get("task_type")
    if task_type is None:
        raise ValueError("task_type is required")

    spider_params = payload.get("spider_params", [])
    if not spider_params:
        raise ValueError(f"spider_params is required when task_type is {task_type}")

    for spider_param in spider_params:
        mall_id = spider_param.get("mall_id")
        if not mall_id:
            raise ValueError("mall_id is required in spider_param")

        spider_cls = get_spider_cls(mall_id, task_type)

        crawl_params = deepcopy(payload)
        crawl_params.pop("spider_params", None)
        crawl_params["spider_param"] = spider_param

        _run_crawl(spider_cls, crawl_params)

    return payload
