"""Main FastAPI application entrypoint for Smart Waste Management System (SWMS).

Provides core REST API routing, CORS middleware, healthcheck probes,
and lifecycle hooks for Day 2 service integrations.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure backend directory and project root are in sys.path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.seed import seed_database
import app.models  # Ensure all models are registered with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.

    Ensures upload directory exists, initializes database tables,
    and runs idempotent master data seeding.
    """
    # Ensure upload directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize database tables and idempotent seeding
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)

    app.state.model_loaded = False
    yield
    app.state.model_loaded = False


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend REST API with AI inference for waste reporting & triage",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js web dashboard local
        "http://127.0.0.1:3000",
        "*",  # Permissive for mobile client in local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Root endpoint welcoming clients and confirming service status."""
    return {
        "status": "success",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Healthcheck endpoint for container orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "service": "backend",
        "version": settings.VERSION,
    }


# Static media serving for uploaded evidence photos
uploads_dir = Path("backend/uploads") if Path("backend/uploads").is_dir() else backend_dir / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
(uploads_dir / "reports").mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory="backend/uploads" if Path("backend/uploads").is_dir() else str(uploads_dir)),
    name="uploads",
)

# Day 2 Router Mounts
from app.api.v1.auth import router as auth_router
from app.api.v1.predict import router as predict_router
from app.api.v1.reports import router as reports_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.categories import router as categories_router
from app.api.v1.users import router as users_router

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(predict_router, prefix=f"{settings.API_V1_STR}/predict", tags=["Prediction"])
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(categories_router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categories"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

