from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["task-tracker"])

# Placeholder route registration for future endpoints

@router.get("/status")
def status() -> dict:
    return {"status": "Task Tracker router is available"}
