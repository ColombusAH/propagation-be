from app.api.v1.endpoints import (alerts, auth, bath_cart, cart, inventory,
                                  network, notifications, payment,
                                  reader_config, rfid_scan, schedules, shifts,
                                  tag_mapping, tag_registration, users, verify)
from fastapi import APIRouter

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
api_router.include_router(network.router, prefix="/network", tags=["network"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(verify.router, prefix="/products", tags=["products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(tag_registration.router)
api_router.include_router(reader_config.router)
api_router.include_router(bath_cart.router)
