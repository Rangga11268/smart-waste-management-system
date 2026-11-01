"""Main FastAPI application entrypoint for Smart Waste Management System (SWMS).

Provides core REST API routing, CORS middleware, healthcheck probes,
and lifecycle hooks for Day 2 service integrations.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.

    In Day 2, PyTorch model weights ('waste_model.pth') will be loaded
    into memory here to ensure zero-latency cold starts for inference.
    """
    # Startup: Load ML model into app.state when ready
    app.state.model_loaded = False
    yield
    # Shutdown: Clean up resources if necessary
    app.state.model_loaded = False


app = FastAPI(
    title="Smart Waste Management System API",
    description="Backend REST API with AI inference for waste reporting & triage",
    version="1.0.0",
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
        "app": "Smart Waste Management System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Healthcheck endpoint for container orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "service": "backend",
        "version": "1.0.0",
    }


# --- Day 2 Router Mount Stubs ---
# from app.api.v1.auth import router as auth_router
# from app.api.v1.predict import router as predict_router
# from app.api.v1.reports import router as reports_router
# from app.api.v1.users import router as users_router
#
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
# app.include_router(predict_router, prefix="/api/v1/predict", tags=["AI Inference"])
# app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
# app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
