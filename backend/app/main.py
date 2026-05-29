from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Task Tracker API")
app.include_router(router)


@app.get("/", summary="Health check")
def health_check() -> dict:
    return {"message": "Task Tracker API running"}
