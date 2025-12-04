"""
Main API router aggregating all v1 endpoints.
"""
from fastapi import APIRouter
from app.api.v1 import auth, uploads, chat, contracts, templates, validation, proposals
from app.api.v1.admin import router as admin_router

# Create main API router
router = APIRouter()

# Include endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
router.include_router(templates.router, prefix="/templates", tags=["Templates"])
router.include_router(validation.router, prefix="/validation", tags=["Validation"])
router.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])
router.include_router(admin_router, prefix="/admin", tags=["Admin"])
