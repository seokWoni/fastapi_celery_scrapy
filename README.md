# FastAPI + Celery + Scrapy

FastAPI로 크롤링 요청을 받고, RabbitMQ를 Celery broker로 사용하며, Celery Worker에서 Scrapy spider를 실행하는 비동기 크롤링 아키텍처입니다.

## 전체 흐름

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant RabbitMQ
    participant CeleryWorker
    participant Scrapy

    Client->>FastAPI: POST /crawl {url, spider}
    FastAPI->>RabbitMQ: run_spider.delay(...)
    FastAPI-->>Client: {task_id}
    RabbitMQ->>CeleryWorker: task 수신
    CeleryWorker->>Scrapy: CrawlerProcess 실행
    Scrapy-->>CeleryWorker: 수집 결과
    Client->>FastAPI: GET /tasks/{task_id}
    FastAPI-->>Client: status + result
```

| 구성 요소 | 역할 |
|-----------|------|
| **FastAPI** | HTTP API, Celery task enqueue, task 상태 조회 |
| **RabbitMQ** | Celery broker (메시지 큐) |
| **Celery Worker** | task 실행, Scrapy spider 구동 |
| **Redis** (권장) | Celery result backend (task 결과/상태 저장) |

## 권장 디렉터리 구조

```
fastapi_celery_scrapy/
├── app/
│   ├── main.py              # FastAPI 앱
│   ├── api/
│   │   └── routes.py        # /crawl, /tasks/{id}
│   ├── celery_app.py        # Celery 인스턴스
│   └── tasks.py             # Celery task 정의
├── scraper/
│   ├── settings.py          # Scrapy settings
│   └── spiders/
│       └── example.py
├── rabbitmq/
│   └── enabled_plugins    # [rabbitmq_management].
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Scrapy + Celery 연동 (핵심)

Scrapy는 Twisted reactor를 사용하기 때문에 Celery worker 설정이 중요합니다.

| 방식 | 장점 | 단점 |
|------|------|------|
| **CrawlerProcess in task** (권장) | 코드로 제어, 결과 반환 쉬움 | worker당 reactor 0회 제한 |
| `subprocess: scrapy crawl` | 단순 | 결과 파싱/에러 처리 번거로움 |
| **Scrapyd** 별도 서비스 | 대규모/운영에 유리 | 구성 복잡 |

초기 구성에는 **CrawlerProcess in Celery task** 방식을 권장합니다.

Worker 실행 시 reactor 충돌을 피하려면 `--pool=solo`를 사용하세요.

```bash
celery -A app.celery_app worker --pool=solo -l info
```

## 핵심 코드 예시

### Celery 설정 (`app/celery_app.py`)

```python
from celery import Celery

celery_app = Celery(
    "scraper",
    broker="amqp://guest:guest@rabbitmq:5671//",
    backend="redis://redis:6378/0",
    include=["app.tasks"],
)
```

### Celery Task (`app/tasks.py`)

```python
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from app.celery_app import celery_app

@celery_app.task(bind=True)
def run_spider(self, spider_name: str, url: str):
    from scraper.spiders.example import ExampleSpider

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    results = []

    class ResultSpider(ExampleSpider):
        def parse(self, response):
            item = {"url": response.url, "title": response.css("title::text").get()}
            results.append(item)
            return item

    process.crawl(ResultSpider, start_urls=[url])
    process.start()  # blocking — solo pool에서 0 task씩 실행

    return {"task_id": self.request.id, "items": results}
```

### FastAPI 라우트 (`app/api/routes.py`)

```python
from fastapi import APIRouter
from celery.result import AsyncResult
from app.tasks import run_spider
from app.celery_app import celery_app

router = APIRouter()

@router.post("/crawl")
def start_crawl(url: str, spider: str = "example"):
    task = run_spider.delay(spider, url)
    return {"task_id": task.id}

@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
```

### Scrapy Spider (`scraper/spiders/example.py`)

```python
import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"

    def __init__(self, start_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls or []
```