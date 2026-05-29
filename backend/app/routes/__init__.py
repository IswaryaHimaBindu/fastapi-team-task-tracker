from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as task_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(task_router)

# Placeholder route registration for future endpoints
@router.get("/status", tags=["task-tracker"])
def status() -> dict:
    return {"status": "Task Tracker router is available"}
