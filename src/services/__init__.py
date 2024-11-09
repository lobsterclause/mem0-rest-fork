"""Services package for memory management."""
import logging
from .memory_service import MemoryService
from src.dependencies import set_memory_service

logger = logging.getLogger(__name__)

def init_services():
    """Initialize all services."""
    try:
        # Create main memory service
        memory_service = MemoryService()
        
        # Set memory service in dependency injection
        set_memory_service(memory_service)
        
        logger.info("Services initialized successfully")
        return memory_service
    
    except Exception as e:
        logger.error(
            "Failed to initialize services: %s",
            str(e),
            exc_info=True
        )
        raise

__all__ = [
    "init_services"
]
