from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Period(BaseModel):
    start_date: str | None = None
    end_date: str | None = None


class ScraperParam(BaseModel):
    mall_id: str
    user_id: str
    goods_ids: list[int] | None = None


class ScrapeJob(BaseModel):
    customer_id: str
    customer_name: str
    task_type: Literal["order", "goods"]
    period: Period = Field(default_factory=Period)
    scraper_params: list[ScraperParam]


class DoRequest(BaseModel):
    order: ScrapeJob
    goods: ScrapeJob

    @model_validator(mode="after")
    def validate_task_types(self) -> "DoRequest":
        if self.order.task_type != "order":
            raise ValueError("order.task_type must be 'order'")
        if self.goods.task_type != "goods":
            raise ValueError("goods.task_type must be 'goods'")
        return self


class DoResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any | None = None
