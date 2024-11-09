"""Routes package for memory system."""
from fastapi import APIRouter

# Create routers
router = APIRouter()

# Import routers after creating main router to avoid circular imports
from .operations import router as operations_router
from .queries import router as queries_router
from .history import router as history_router
from .memories import router as memories_router
from .suggestions import router as suggestions_router
from .compression import router as compression_router
from .bridge import router as bridge_router
from .websocket import router as websocket_router

# Include sub-routers
router.include_router(operations_router, prefix="/operations", tags=["operations"])
router.include_router(queries_router, prefix="/queries", tags=["queries"])
router.include_router(history_router, prefix="/history", tags=["history"])
router.include_router(memories_router, prefix="/memories", tags=["memories"])
router.include_router(suggestions_router, prefix="/suggestions", tags=["suggestions"])
router.include_router(compression_router, prefix="/compression", tags=["compression"])
router.include_router(bridge_router, prefix="/bridge", tags=["bridge"])
router.include_router(websocket_router, prefix="/ws", tags=["websocket"])
