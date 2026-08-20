from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="FastAPI Celery Scrapy")
app.include_router(router)


@app.get("/")
def read_root():
    return {
        "message": "API is running",
        "docs": "/docs",
        "redoc": "/redoc",
        "routes": [
            {"method": "POST", "path": "/do"},
            {"method": "GET", "path": "/tasks/{task_id}"},
        ],
    }
