from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Task
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
        return task

    def get_task(self, db: Session, task_id: int) -> Task:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        return task

    def list_tasks(self, db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
        return db.query(Task).offset(skip).limit(limit).all()

    def update_task(self, db: Session, task_id: int, payload: TaskUpdate) -> Task:
        task = self.get_task(db, task_id)
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
        return task

    def delete_task(self, db: Session, task_id: int) -> None:
        task = self.get_task(db, task_id)
        db.delete(task)
        db.commit()
