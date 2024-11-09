"""Main application module."""
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .middleware.auth import get_current_user
from .middleware.rate_limit import check_http_rate_limit
from .middleware.error_handlers import (
    error_handler,
    http_exception_handler,
    startup_exception_handler,
    shutdown_exception_handler
)
from .services import init_services
from .dependencies import get_memory_service
from .routes import router as api_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Memory Service",
        description="REST API for memory operations",
        version=settings.api_version,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
        allow_credentials=True
    )

    # Add middleware dependencies
    async def auth_dependency(request: Request):
        """Authentication dependency."""
        return await get_current_user(request)

    async def rate_limit_dependency(request: Request):
        """Rate limiting dependency."""
        await check_http_rate_limit(request)

    # Add exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle all uncaught exceptions."""
        return await http_exception_handler(request, exc)

    # Add startup event handler
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        try:
            # Initialize services
            init_services()
            
            logger.info("Application started successfully")
        
        except Exception as e:
            logger.error(
                "Failed to start application: %s",
                str(e),
                exc_info=True
            )
            await startup_exception_handler(e)

    # Add shutdown event handler
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown."""
        try:
            # Get memory service
            memory_service = get_memory_service()
            
            # Clean up resources
            await memory_service.cleanup()
            
            logger.info("Application shut down successfully")
        
        except Exception as e:
            logger.error(
                "Failed to shut down application: %s",
                str(e),
                exc_info=True
            )
            await shutdown_exception_handler(e)

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    # Include API router with dependencies
    app.include_router(
        api_router,
        prefix=settings.api_prefix,
        dependencies=[
            Depends(auth_dependency),
            Depends(rate_limit_dependency)
        ]
    )

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug
    )
