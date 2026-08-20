"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.cms import router as cms_router
from app.api.v1.settings import router as settings_router
from app.api.v1.contact import router as contact_router
from app.api.v1.upload import router as upload_router
from app.api.v1.profile import router as profile_router
from app.api.v1.health import router as health_router
from app.api.v1.device_token import router as device_token_router
from app.api.v1.calculation import router as calculation_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(cms_router, prefix="/cms", tags=["CMS"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(contact_router, prefix="/contact", tags=["Contact"])
api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
api_router.include_router(profile_router, prefix="/profile", tags=["Profile"])
api_router.include_router(device_token_router, prefix="/device-token", tags=["Device Token"])
api_router.include_router(calculation_router, prefix="/calculation", tags=["Calculation"])
