from copy import deepcopy
from typing import Any

from billiard import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from worker.celery_app import celery_app
from worker.scrapy.spiders import BaseSpider

def _run_crawl(spider_cls: Any, params: dict[str, Any]) -> None:
    """billiard Process용 탑레벨 함수 (바인드 메서드는 pickle 이슈 있음)."""
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl(spider_cls, **params)
    crawler.start()

class RunCrawlerProcess:
    def __init__(self, spider_cls: Any | None = None):
        self.spider_cls = spider_cls

    def crawl(self, params: dict[str, Any]) -> None:
        if self.spider_cls is None:
            raise ValueError("spider_cls is required")
        process = Process(target=_run_crawl, args=(self.spider_cls, params))
        process.start()
        process.join()

@celery_app.task(bind=True)
def do_spider(self, payload: dict[str, Any]):
    task_type = payload.get("task_type", None)

    if task_type is None:
        raise ValueError(f"unknown spider: {task_type}")

    spider_params = payload.get("spider_params", [])
    if not spider_params:
        raise ValueError(f"spider_params is required when task_type is {task_type}")

    crawler_process = RunCrawlerProcess(spider_cls=get_spider_cls(mall_id, task_type))

    items: list[dict[str, Any]] = []

    for spider_param in spider_params:
        base_params = deepcopy(payload)
        base_params.pop("spider_params", None)
        base_params["spider_param"] = spider_param
        crawler_process.crawl(base_params)

    return items

def get_spider_cls(mall_id: str, task_type: str) -> Any:
    module_path = f"worker.scrapy.spiders.{mall_id}.{task_type}"

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise ValueError(f"spider module not found: {module_path}") from exc

    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseSpider) and obj is not BaseSpider and obj.__module__ == module_path:
            return obj
    else:
        raise ValueError(f"BaseSpider subclass not found in {module_path}")