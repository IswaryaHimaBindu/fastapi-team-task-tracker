from datetime import date, datetime
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.core.cache import cache_service
from app.models import PriorityEnum, Task, TaskStatusEnum, User
from app.schemas.task import TaskAnalyticsItem, TaskCreate, TaskUpdate


class TaskService:
    def _invalidate_task_list_cache(self, *assignee_ids: Optional[int]) -> None:
        for assignee_id in {assignee_id for assignee_id in assignee_ids if assignee_id is not None}:
            cache_service.delete_task_list(assignee_id)

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
        self._invalidate_task_list_cache(task.assignee_id)
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

    def update_task(self, db: Session, task_id: int, payload: TaskUpdate) -> Tuple[Task, Optional[int]]:
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

        self._invalidate_task_list_cache(previous_assignee_id, task.assignee_id)
        return task, previous_assignee_id

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
        if new_status == TaskStatusEnum.DONE:
            task.completed_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)

        self._invalidate_task_list_cache(task.assignee_id)
        return task

    def delete_task(self, db: Session, task_id: int) -> None:
        task = self.get_task(db, task_id)
        assignee_id = task.assignee_id
        db.delete(task)
        db.commit()
        self._invalidate_task_list_cache(assignee_id)

    def get_task_analytics(self, db: Session) -> list[TaskAnalyticsItem]:
        completed_duration_seconds = func.date_part(
            'epoch',
            Task.completed_at - Task.created_at,
        )

        query = (
            db.query(
                Task.assignee_id.label('user_id'),
                User.first_name,
                User.last_name,
                func.sum(
                    case(
                        [
                            (
                                and_(
                                    Task.due_date < func.current_date(),
                                    Task.status != TaskStatusEnum.DONE,
                                ),
                                1,
                            )
                        ],
                        else_=0,
                    )
                ).label('overdue_count'),
                func.avg(
                    case(
                        [
                            (
                                and_(
                                    Task.status == TaskStatusEnum.DONE,
                                    Task.completed_at.isnot(None),
                                ),
                                completed_duration_seconds,
                            )
                        ],
                        else_=None,
                    )
                ).label('avg_completion_seconds'),
            )
            .join(User, User.id == Task.assignee_id)
            .filter(Task.assignee_id.isnot(None))
            .group_by(Task.assignee_id, User.first_name, User.last_name)
        )

        results = []
        for row in query:
            average_days = None
            if row.avg_completion_seconds is not None:
                average_days = float(row.avg_completion_seconds) / 86400.0
            results.append(
                TaskAnalyticsItem(
                    user_id=row.user_id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    overdue_count=int(row.overdue_count or 0),
                    average_completion_days=average_days,
                )
            )
        return results
