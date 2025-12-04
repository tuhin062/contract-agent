"""Admin API endpoints."""
from fastapi import APIRouter
from app.api.v1.admin import users, settings, audit

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["Admin - Users"])
router.include_router(settings.router, prefix="/settings", tags=["Admin - Settings"])
router.include_router(audit.router, prefix="/audit", tags=["Admin - Audit"])

