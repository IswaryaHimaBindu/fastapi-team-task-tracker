from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import StandardResponse
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
) -> StandardResponse[TaskListResponse]:
    tasks = task_service.list_tasks(db, skip=skip, limit=limit)
    return StandardResponse(data=TaskListResponse(items=tasks, total=len(tasks)))


@router.get("/{task_id}", response_model=StandardResponse[TaskResponse])
def get_task(task_id: int, db: Session = Depends(get_db)) -> StandardResponse[TaskResponse]:
    task = task_service.get_task(db, task_id)
    return StandardResponse(data=task)


@router.put("/{task_id}", response_model=StandardResponse[TaskResponse])
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> StandardResponse[TaskResponse]:
    task = task_service.update_task(db, task_id, payload)
    return StandardResponse(data=task)


@router.delete("/{task_id}", response_model=StandardResponse[dict])
def delete_task(task_id: int, db: Session = Depends(get_db)) -> StandardResponse[dict]:
    task_service.delete_task(db, task_id)
    return StandardResponse(data={"message": "Task deleted successfully."})
