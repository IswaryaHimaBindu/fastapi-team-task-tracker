from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import StandardResponse
from app.schemas.task import TaskAnalyticsResponse
from app.services.tasks import TaskService

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = TaskService()


@router.get("/tasks", response_model=StandardResponse[TaskAnalyticsResponse])
def get_task_analytics(db: Session = Depends(get_db)) -> StandardResponse[TaskAnalyticsResponse]:
    analytics_items = analytics_service.get_task_analytics(db)
    return StandardResponse(data=TaskAnalyticsResponse(items=analytics_items))
