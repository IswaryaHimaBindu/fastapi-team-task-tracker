from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.cache import cache_service
from app.models import PriorityEnum, Task, TaskStatusEnum
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def create_task(self, db: Session, payload: TaskCreate) -> Task:
        task = Task(
            title=payload.title,
            description=payload.description,
            project_id=payload.project_id,
            assignee_id=payload.assignee_id,
            creator_id=payload.creator_id,
            due_date=payload.due_date,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        if task.assignee_id is not None:
            cache_service.delete_task_list(task.assignee_id)
        return task

    def get_task(self, db: Session, task_id: int) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        return task

    def list_tasks(
        self,
        db: Session,
        page: int = 1,
        limit: int = 100,
        status: Optional[TaskStatusEnum] = None,
        priority: Optional[PriorityEnum] = None,
        assignee_id: Optional[int] = None,
        due_date: Optional[date] = None,
    ) -> tuple[list[Task], int]:
        query = db.query(Task)

        if status is not None:
            query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        if assignee_id is not None:
            query = query.filter(Task.assignee_id == assignee_id)
        if due_date is not None:
            query = query.filter(Task.due_date == due_date)

        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()
        return items, total

    def update_task(self, db: Session, task_id: int, payload: TaskUpdate) -> Task:
        task = self.get_task(db, task_id)
        previous_assignee_id = task.assignee_id

        if payload.title is not None:
            task.title = payload.title
        if payload.description is not None:
            task.description = payload.description
        if payload.project_id is not None:
            task.project_id = payload.project_id
        if payload.assignee_id is not None:
            task.assignee_id = payload.assignee_id
        if payload.creator_id is not None:
            task.creator_id = payload.creator_id
        if payload.due_date is not None:
            task.due_date = payload.due_date

        db.add(task)
        db.commit()
        db.refresh(task)

        if previous_assignee_id is not None:
            cache_service.delete_task_list(previous_assignee_id)
        if task.assignee_id is not None:
            cache_service.delete_task_list(task.assignee_id)

        return task

    def update_task_status(
        self,
        db: Session,
        task_id: int,
        new_status: TaskStatusEnum,
        acting_user_id: int,
        acting_user_role: str,
    ) -> Task:
        task = self.get_task(db, task_id)

        if task.assignee_id != acting_user_id and acting_user_role != "MANAGER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assignee or a manager may update task status.",
            )

        current_status = TaskStatusEnum(task.status)
        if current_status == new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already in the requested status.",
            )

        allowed_transitions = {
            TaskStatusEnum.TODO: {TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.BLOCKED},
            TaskStatusEnum.IN_PROGRESS: {TaskStatusEnum.IN_REVIEW, TaskStatusEnum.BLOCKED},
            TaskStatusEnum.IN_REVIEW: {TaskStatusEnum.DONE, TaskStatusEnum.BLOCKED},
            TaskStatusEnum.DONE: set(),
            TaskStatusEnum.BLOCKED: set(),
        }

        if new_status not in allowed_transitions.get(current_status, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status.value} to {new_status.value}.",
            )

        task.status = new_status
        db.add(task)
        db.commit()
        db.refresh(task)

        if task.assignee_id is not None:
            cache_service.delete_task_list(task.assignee_id)

        return task

    def delete_task(self, db: Session, task_id: int) -> None:
        task = self.get_task(db, task_id)
        assignee_id = task.assignee_id
        db.delete(task)
        db.commit()
        if assignee_id is not None:
            cache_service.delete_task_list(assignee_id)
