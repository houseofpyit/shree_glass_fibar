"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pathlib import Path

from app.config import settings
from app.api.v1 import api_router
from app.middleware.security import SecurityHeadersMiddleware
from app.core.response import error_response
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")

    # Create upload directories
    Path(settings.UPLOAD_PATH, "images").mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_PATH, "pdfs").mkdir(parents=True, exist_ok=True)

    # Auto-create tables in development (for SQLite or first-run convenience)
    if settings.ENVIRONMENT == "development":
        from app.database import engine, Base
        from app.models.user import User  # noqa: F401
        from app.models.app_settings import AppSettings  # noqa: F401
        from app.models.cms_page import CMSPage  # noqa: F401
        from app.models.contact_information import ContactInformation  # noqa: F401
        from app.models.audit_log import AuditLog  # noqa: F401
        from app.models.device_token import DeviceToken  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Production-ready FastAPI backend for Shree Glass Fiber mobile application. "
            "Provides user management, CMS, authentication, and admin APIs."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Middleware (order matters: last added = first executed)
    app.add_middleware(SecurityHeadersMiddleware)

    # Bearer-token APIs work without cookies; allow public GET from any origin
    # (including LAN hosts such as http://192.168.1.2:8082).
    allow_all_origins = (
        not settings.is_production
        or settings.CORS_ORIGINS == ["*"]
        or "*" in settings.CORS_ORIGINS
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all_origins else settings.CORS_ORIGINS,
        allow_credentials=not allow_all_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure for your domain
        )

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Format HTTP exceptions (including 409 Conflict) with a `message` field."""
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(message=str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error["loc"])
            errors.append(f"{loc}: {error['msg']}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(message="Validation error", errors=errors),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(message="Internal server error"),
        )

    # Routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Static files (uploads)
    upload_path = Path(settings.UPLOAD_PATH)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount(
        f"/{settings.UPLOAD_PATH}",
        StaticFiles(directory=str(upload_path)),
        name="uploads",
    )

    return app


app = create_app()
