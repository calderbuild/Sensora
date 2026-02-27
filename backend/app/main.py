"""
Aether FastAPI Application Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import calibration, formulation, payment

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Driven Adaptive Perfume Formulation Platform",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sensora.vercel.app",
        "https://*.vercel.app",  # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(calibration.router, prefix=f"{settings.api_prefix}/calibration", tags=["calibration"])
app.include_router(formulation.router, prefix=f"{settings.api_prefix}/formulation", tags=["formulation"])
app.include_router(payment.router, prefix=f"{settings.api_prefix}/payment", tags=["payment"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "api": "ok",
            "chromadb": "ok"
        }
    }
