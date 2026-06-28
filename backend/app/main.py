"""FastAPI main application module."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.database import create_tables, get_db
from app.routers import auth, profile, schemes, eligibility, chat, applications, products

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    logger.info("Starting up SBI Saathi Backend...")
    # Initialize database tables
    await create_tables()
    
    # Seed scheme data if necessary
    from app.routers.schemes import seed_schemes
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await seed_schemes(db)
        
    yield
    logger.info("Shutting down SBI Saathi Backend...")


app = FastAPI(
    title="SBI Saathi API",
    description="Backend API for SBI Saathi Government Benefit Assistant",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "SBI Saathi Backend"}


# Include Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(profile.router, prefix=settings.API_PREFIX)
app.include_router(schemes.router, prefix=settings.API_PREFIX)
app.include_router(eligibility.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(applications.router, prefix=settings.API_PREFIX)
app.include_router(products.router, prefix=settings.API_PREFIX)

