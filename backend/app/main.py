from fastapi import FastAPI
from starlette.middleware import Middleware

from app.middleware.error_handler import GlobalExceptionHandlerMiddleware
from app.middleware.rbac import RBACMiddleware
from app.routes import router
from app.routes.analytics import router as analytics_router
from app.routes.websocket import router as websocket_router

middleware = [
    Middleware(GlobalExceptionHandlerMiddleware),
    Middleware(RBACMiddleware),
]

app = FastAPI(title="Task Tracker API", middleware=middleware)
app.include_router(router)
app.include_router(analytics_router)
app.include_router(websocket_router)


@app.get("/", summary="Health check")
def health_check() -> dict:
    return {"message": "Task Tracker API running"}
