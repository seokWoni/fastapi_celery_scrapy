from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Period(BaseModel):
    start_date: str | None = None
    end_date: str | None = None


class Param(BaseModel):
    mall_id: str
    goods_ids: list[Any] | None = None


class DoRequest(BaseModel):
    customer_id: str
    customer_name: str
    task_type: Literal["order", "goods"]
    period: Period = Field(default_factory=Period)
    params: list[Param]

    @model_validator(mode="after")
    def validate_period_by_task_type(self) -> "DoRequest":
        if self.task_type == "order":
            if not self.period.start_date or not self.period.end_date:
                raise ValueError(
                    "period.start_date and period.end_date are required when task_type is 'order'"
                )
        return self


class DoResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any | None = None
