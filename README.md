# FastAPI + Celery + Scrapy

FastAPI로 크롤링 요청을 받고, RabbitMQ를 Celery broker로 사용하며, Celery Worker에서 Scrapy spider를 실행하는 비동기 크롤링 애플리케이션입니다.

Docker Compose 실행 방법은 프로젝트 루트 [`README.md`](../README.md)를 참고하세요.

## 현재 구현

- [x] FastAPI API
- [x] Celery 연동
- [x] RabbitMQ
- [x] Redis
- [x] Scrapy
- [x] BaseSpider 구조
- [x] Docker Compose
- [x] 작업 종류별 Queue 분리
- [ ] Main DB / Customer DB
- [ ] Scrapy Pipeline DB 저장

## 전체 흐름

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant RabbitMQ
    participant CeleryWorker
    participant Scrapy
    participant MySQL

    Client->>FastAPI: POST /do {task_type, spider_params, ...}
    FastAPI->>RabbitMQ: do_spider.delay(payload)
    FastAPI-->>Client: {task_id}
    RabbitMQ->>CeleryWorker: task 수신
    CeleryWorker->>Scrapy: mall_id + task_type으로 spider 실행
    Scrapy-->>CeleryWorker: 수집 결과
    CeleryWorker->>MySQL: task result 저장
    Client->>FastAPI: GET /tasks/{task_id}
    FastAPI-->>Client: status + result
```

| 구성 요소 | 역할 |
|-----------|------|
| **FastAPI** (`app/`) | HTTP API, Celery task enqueue, task 상태 조회 |
| **RabbitMQ** | Celery broker (메시지 큐) |
| **Celery Worker** (`worker/`) | task 실행, Scrapy spider 구동 |
| **MySQL** | Celery result backend (`db+mysql+pymysql://...`) |
| **Redis** | Compose에 포함 (추가 용도 확장 가능) |

## 디렉터리 구조

```
src/
├── app/                          # FastAPI
│   ├── main.py
│   ├── schemas.py                # 요청/응답 스키마
│   └── api/
│       └── routes.py             # POST /do, GET /tasks/{id}
├── worker/                       # Celery + Scrapy
│   ├── celery_app.py
│   ├── celeryconfig.py
│   ├── tasks.py                  # do_spider task
│   ├── db.py                     # SQLAlchemy DB 헬퍼
│   ├── .env                      # broker, result backend, DB, Scrapy settings
│   └── scrapy/
│       ├── settings.py
│       ├── spiders/
│       │   ├── __init__.py       # BaseSpider
│       │   └── mall0001/
│       │       ├── order.py
│       │       └── goods.py
│       └── pipelines/
│           ├── __init__.py       # BasePipeline
│           └── mall0001/
│               ├── order.py
│               └── goods.py
├── env.py
└── .env
```

## API

### POST /do

주문(`order`) 또는 상품(`goods`) 수집 요청을 Celery task 하나로 전달합니다.

```json
{
  "customer_id": "asdf",
  "customer_name": "테스트",
  "task_type": "order",
  "period": {
    "start_date": "20260815",
    "end_date": "20260825"
  },
  "spider_params": [
    {
      "mall_id": "mall0001",
      "user_id": "user1"
    },
    {
      "mall_id": "mall0001",
      "user_id": "user2",
      "goods_list": [
        { "goods_id": "1", "option_id": [1, 2] }
      ]
    }
  ]
}
```

- `task_type: "order"` → `period.start_date`, `period.end_date` 필수 (YYYYMMDD)
- `task_type: "goods"` → `period` 선택
- `spider_params[].goods_list` → 상품 수집 시 사용

응답: `{ "task_id": "...", "status": "PENDING" }`

### GET /tasks/{task_id}

Celery task 상태 및 결과 조회 (MySQL result backend).

## Celery + Scrapy 연동

### Task 실행 (`worker/tasks.py`)

1. `payload.spider_params`를 순회
2. 각 param의 `mall_id` + payload의 `task_type`으로 spider 클래스 탐색  
   → `worker.scrapy.spiders.{mall_id}.{task_type}`
3. `billiard.Process` + `CrawlerProcess`로 spider 실행 (reactor 충돌 방지)
4. 모든 프로세스 `join()` 후 payload 반환

Worker는 `--pool=solo`로 실행합니다.

```bash
celery -A worker.celery_app worker --pool=solo -l info
```

### Spider 구조 (`BaseSpider`)

하위 mall spider는 `name`, `custom_settings`(파이프라인)만 정의하고, `start_requests` / `parse`를 mall별로 구현합니다.

공통으로 `self`에 다음이 설정됩니다.

- `customer_id`, `customer_name`, `task_type`
- `mall_id`, `user_id`, `spider_param`, `goods_list`
- `self.db` — `worker.db.Database` 인스턴스

새 mall 추가 예:

```
worker/scrapy/spiders/mall0002/order.py
worker/scrapy/spiders/mall0002/goods.py
worker/scrapy/pipelines/mall0002/order.py
worker/scrapy/pipelines/mall0002/goods.py
```

### Pipeline 구조 (`BasePipeline`)

- `open_spider` — DB 연결, spider 컨텍스트(customer/mall/user) 저장
- `close_spider` — `flush()` 후 DB 연결 종료
- `process_item` / `flush` — mall별 pipeline에서 구현 (DB 저장 예정)

## 환경 변수

| 파일 | 용도 |
|------|------|
| `src/.env` | 앱 공통 (선택) |
| `src/worker/.env` | Celery broker/backend, Scrapy settings, DB 접속 |
| `../.env` (프로젝트 루트) | Docker Compose — RabbitMQ, MySQL 컨테이너 |

`worker/.env` 예시:

```env
CELERY_BROKER_URL=amqp://admin:admin@rabbitmq:5672//
CELERY_RESULT_BACKEND=db+mysql+pymysql://admin:admin@db:3306/celery_scrapy
SCRAPY_SETTINGS_MODULE=worker.scrapy.settings

DB_HOST=db
DB_PORT=3306
DB_NAME=celery_scrapy
DB_USER=admin
DB_PASSWORD=!dnjs12
```

## 로컬 실행 (Docker 없이)

```bash
cd src

# FastAPI
uvicorn app.main:app --reload

# Celery Worker (별도 터미널, RabbitMQ·MySQL 필요)
celery -A worker.celery_app worker --pool=solo -l info
```

## 향후 작업

| 항목 | 설명 |
|------|------|
| **작업 종류별 Queue 분리** | `order` / `goods` 등 task_type별 Celery queue·worker 분리 (`celeryconfig.task_routes` 확장) |
| **Main DB / Customer DB** | 고객별 DB 분리, spider/pipeline에서 customer_id 기준 라우팅 |
| **Scrapy Pipeline DB 저장** | `BasePipeline.flush()`에 실제 INSERT/UPSERT 구현, mall별 테이블 스키마 정의 |
