from app.routers.auth import router as auth_router
from app.routers.cameras import router as cameras_router
from app.routers.incidents import router as incidents_router
from app.routers.responders import router as responders_router
from app.routers.locations import router as locations_router
from app.routers.notifications import router as notifications_router
from app.routers.demo import router as demo_router

__all__ = [
    "auth_router",
    "cameras_router",
    "incidents_router",
    "responders_router",
    "locations_router",
    "notifications_router",
    "demo_router"
]
