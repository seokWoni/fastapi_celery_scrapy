from celery.result import AsyncResult
from fastapi import APIRouter

from app.celery_app import celery_app
from app.schemas import DoRequest, DoResponse, TaskStatusResponse
from app.tasks import process_do

router = APIRouter()


@router.post("/do", response_model=DoResponse)
def do(payload: DoRequest) -> DoResponse:
    task = process_do.delay(
        order=payload.order.model_dump(),
        goods=payload.goods.model_dump(),
    )
    return DoResponse(task_id=task.id, status=task.status)


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=result.result if result.ready() else None,
    )
