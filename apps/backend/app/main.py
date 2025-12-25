"""
aboutai Backend API
===========================================
The autonomous content pipeline for the AI Trust Engine.

Endpoints:
- /api/v1/search - Search using SearXNG
- /api/v1/analyze - Analyze tools for wrapper detection
- /api/v1/pipeline - Trigger content pipeline
- /api/v1/drafts - Manage content drafts
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.api.routes import router as api_router


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if not settings.DEBUG else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(
        "Starting aboutai backend",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )
    
    yield
    
    # Shutdown
    logger.info("Shutting down aboutai backend")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # aboutai Backend API
    
    The autonomous content pipeline for the AI Trust Engine.
    
    ## Features
    
    - **Search**: Self-hosted search using SearXNG
    - **Trust Engine**: Automated wrapper detection and trust scoring
    - **Content Pipeline**: Autonomous news and tool ingestion
    - **Publishing**: MDX content generation for frontend
    
    ## Key Endpoints
    
    - `POST /api/v1/search` - Search for AI tools and news
    - `POST /api/v1/analyze` - Analyze a tool URL for wrapper detection
    - `POST /api/v1/pipeline/run` - Trigger the content pipeline
    - `GET /api/v1/drafts` - List content drafts pending review
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "Request processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=round(process_time * 1000, 2),
    )
    
    return response


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ===========================================
# Root Endpoints
# ===========================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies all dependencies are available"""
    import httpx
    
    checks = {
        "api": True,
        "redis": False,
        "searxng": False,
    }
    
    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = True
    except Exception:
        pass
    
    # Check SearXNG
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.SEARXNG_URL}/healthz", timeout=5)
            checks["searxng"] = response.status_code == 200
    except Exception:
        pass
    
    all_ready = all(checks.values())
    
    return JSONResponse(
        status_code=200 if all_ready else 503,
        content={
            "ready": all_ready,
            "checks": checks,
        },
    )


# ===========================================
# Error Handlers
# ===========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
