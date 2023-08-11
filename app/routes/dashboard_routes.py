import os
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dummy data for tasks
tasks = []  # Will be populated from the database

# Database connection details
DATABASE_URL = os.environ.get("DATABASE_URL")

# Redis connection details
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")

@router.on_event("startup")
async def startup_event():
    global tasks
    tasks = await get_tasks_from_db()
    # Using Redis to get total tasks and recent tasks
    total_tasks_redis = get_total_tasks_from_redis()
    recent_tasks_redis = get_recent_tasks_from_redis()


@router.get("/admin/")
def admin_dashboard(request: Request):
    total_tasks_redis = get_total_tasks_from_redis()
    recent_tasks_redis = get_recent_tasks_from_redis()
    return templates.TemplateResponse("dashboard.html", {"request": request, "total_tasks_redis": total_tasks_redis, "recent_tasks_redis": recent_tasks_redis})


@router.get("/admin/tasks/")
def admin_tasks(request: Request):
    return {"tasks": tasks}

@router.get("/", response_class=HTMLResponse, tags=["dashboard"])
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "data": get_dashboard_data()})
