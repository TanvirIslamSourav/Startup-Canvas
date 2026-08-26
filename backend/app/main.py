"""FastAPI application factory."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging, get_logger
from app.routers import activity as activity_router
from app.routers import ai as ai_router
from app.routers import business_canvas as bc_router
from app.routers import competitor as competitor_router
from app.routers import customer_persona as persona_router
from app.routers import document as document_router
from app.routers import health as health_router
from app.routers import idea as idea_router
from app.routers import lean_canvas as lc_router
from app.routers import milestone as milestone_router
from app.routers import note as note_router
from app.routers import progress_tracker as pt_router
from app.routers import roadmap as roadmap_router
from app.routers import startup_project as project_router
from app.routers import swot as swot_router
from app.routers import task as task_router
from app.routers import user as user_router

logger = get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    logger.info(
        "startup",
        environment=settings.environment,
        advisor=settings.startup_advisor_provider,
    )
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Startup Canvas API",
        version="0.1.0",
        description=(
            "Backend for the Startup Canvas application. "
            "All endpoints are under `/api/v1`."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers ----------------------------------------------------
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content={"error": exc.to_dict()},
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Internal server error"}},
        )

    # Routers ---------------------------------------------------------------
    api_prefix = settings.api_prefix
    app.include_router(health_router.router, prefix=api_prefix)
    app.include_router(ai_router.router, prefix=api_prefix)
    app.include_router(idea_router.router, prefix=api_prefix)
    app.include_router(project_router.router, prefix=api_prefix)
    app.include_router(user_router.router, prefix=api_prefix)
    app.include_router(lc_router.router, prefix=api_prefix)
    app.include_router(bc_router.router, prefix=api_prefix)
    app.include_router(swot_router.router, prefix=api_prefix)
    app.include_router(pt_router.router, prefix=api_prefix)
    app.include_router(competitor_router.router, prefix=api_prefix)
    app.include_router(persona_router.router, prefix=api_prefix)
    app.include_router(task_router.router, prefix=api_prefix)
    app.include_router(milestone_router.router, prefix=api_prefix)
    app.include_router(document_router.router, prefix=api_prefix)
    app.include_router(note_router.router, prefix=api_prefix)
    app.include_router(roadmap_router.router, prefix=api_prefix)
    app.include_router(activity_router.router, prefix=api_prefix)

    @app.get("/", include_in_schema=False)
    def root() -> dict:
        return {
            "name": "Startup Canvas API",
            "version": "0.1.0",
            "docs": "/docs",
            "api": api_prefix,
        }

    return app


app = create_app()