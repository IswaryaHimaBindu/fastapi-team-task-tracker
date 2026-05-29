from fastapi import FastAPI
from starlette.middleware import Middleware

from app.middleware.rbac import RBACMiddleware
from app.routes import router

middleware = [Middleware(RBACMiddleware)]

app = FastAPI(title="Task Tracker API", middleware=middleware)
app.include_router(router)


@app.get("/", summary="Health check")
def health_check() -> dict:
    return {"message": "Task Tracker API running"}
