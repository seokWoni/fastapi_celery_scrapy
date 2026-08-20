from typing import Any

from app.celery_app import celery_app


@celery_app.task(bind=True, name="app.tasks.process_do")
def process_do(self, order: dict[str, Any], goods: dict[str, Any]):
    """주문과 상품을 한 번에 받아 처리합니다."""
    return {
        "task_id": self.request.id,
        "order": order,
        "goods": goods,
    }
