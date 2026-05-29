from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import StandardResponse
from app.models import PriorityEnum, TaskStatusEnum
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service = TaskService()


@router.post("/", response_model=StandardResponse[TaskResponse], status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> StandardResponse[TaskResponse]:
    task = task_service.create_task(db, payload)
    return StandardResponse(data=task)


@router.get("/", response_model=StandardResponse[TaskListResponse])
def list_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=200),
    status: Optional[TaskStatusEnum] = Query(None),
    priority: Optional[PriorityEnum] = Query(None),
    assignee_id: Optional[int] = Query(None, ge=1),
    due_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
) -> StandardResponse[TaskListResponse]:
    tasks, total = task_service.list_tasks(
        db,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        due_date=due_date,
    )
    return StandardResponse(data=TaskListResponse(items=tasks, total=total, page=page, limit=limit))


@router.get("/{task_id}", response_model=StandardResponse[TaskResponse])
def get_task(task_id: int, db: Session = Depends(get_db)) -> StandardResponse[TaskResponse]:
    task = task_service.get_task(db, task_id)
    return StandardResponse(data=task)


@router.put("/{task_id}", response_model=StandardResponse[TaskResponse])
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> StandardResponse[TaskResponse]:
    task = task_service.update_task(db, task_id, payload)
    return StandardResponse(data=task)


@router.patch("/{task_id}/status", response_model=StandardResponse[TaskResponse])
def update_task_status(
    request: Request,
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
) -> StandardResponse[TaskResponse]:
    user_id = request.state.user_id
    user_role = request.state.user_role
    if user_id is None or user_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User credentials are required to update task status.",
        )

    task = task_service.update_task_status(
        db,
        task_id,
        payload.status,
        int(user_id),
        user_role,
    )
    return StandardResponse(data=task)


@router.delete("/{task_id}", response_model=StandardResponse[dict])
def delete_task(task_id: int, db: Session = Depends(get_db)) -> StandardResponse[dict]:
    task_service.delete_task(db, task_id)
    return StandardResponse(data={"message": "Task deleted successfully."})
