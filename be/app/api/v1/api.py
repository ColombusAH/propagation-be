from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, schedules, shifts, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(shifts.router, prefix="/shifts", tags=["shifts"]) 