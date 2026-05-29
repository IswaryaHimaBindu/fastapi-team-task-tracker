from fastapi import APIRouter

from .auth import router as auth_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)

# Placeholder route registration for future endpoints
@router.get("/status", tags=["task-tracker"])
def status() -> dict:
    return {"status": "Task Tracker router is available"}
