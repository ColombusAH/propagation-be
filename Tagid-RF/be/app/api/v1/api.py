from fastapi import APIRouter

from app.api.v1.endpoints import alerts, auth, payment, rfid_scan, schedules, shifts, tag_mapping, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(shifts.router, prefix="/shifts", tags=["shifts"])
api_router.include_router(tag_mapping.router)
api_router.include_router(rfid_scan.router)
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
