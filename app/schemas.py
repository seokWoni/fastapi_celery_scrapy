from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Period(BaseModel):
    start_date: str | None = None
    end_date: str | None = None


class Goods(BaseModel):
    goods_id: str
    option_id : list[int] | None = None

class SpiderParam(BaseModel):
    mall_id: str
    user_id: str
    goods_list: list[Goods] | None = None

class DoRequest(BaseModel):
    customer_id: str
    customer_name: str
    task_type: Literal["order", "goods"]
    period: Period = Field(default_factory=Period)
    spider_params: list[SpiderParam]

    @staticmethod
    def _require_yyyymmdd(field_name: str, value: str) -> None:
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError:
            raise ValueError(f"{field_name} must be YYYYMMDD format, got: {value!r}")

    @model_validator(mode="after")
    def validate_period_by_task_type(self) -> "DoRequest":
        if self.task_type != "order":
            return self

        if not self.period.start_date or not self.period.end_date:
            raise ValueError(
                "period.start_date and period.end_date are required when task_type is 'order'"
            )

        self._require_yyyymmdd("period.start_date", self.period.start_date)
        self._require_yyyymmdd("period.end_date", self.period.end_date)
        return self


class DoResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any | None = None
