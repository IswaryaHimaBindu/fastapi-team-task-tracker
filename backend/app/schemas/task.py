from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    project_id: int
    assignee_id: int | None = None
    creator_id: int | None = None
    due_date: date | None = None

    @validator("due_date")
    def due_date_must_be_future(cls, value: date | None) -> date | None:
        if value is not None and value <= date.today():
            raise ValueError("due_date must be a future date")
        return value


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1)
    description: str | None = None
    project_id: int | None = None
    assignee_id: int | None = None
    creator_id: int | None = None
    due_date: date | None = None

    @validator("due_date")
    def due_date_must_be_future(cls, value: date | None) -> date | None:
        if value is not None and value <= date.today():
            raise ValueError("due_date must be a future date")
        return value


class TaskResponse(TaskBase):
    id: int
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
