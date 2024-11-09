"""Dependencies for the application."""
from typing import Optional
from src.services.memory_service import MemoryService
from src.services.types import MemoryServiceProtocol

# Global service instance
_memory_service: Optional[MemoryServiceProtocol] = None

def set_memory_service(service: MemoryServiceProtocol) -> None:
    """Set the global memory service instance."""
    global _memory_service
    _memory_service = service

def get_memory_service() -> MemoryServiceProtocol:
    """Get memory service dependency."""
    if _memory_service is None:
        raise RuntimeError("Memory service not initialized")
    return _memory_service

__all__ = [
    "get_memory_service",
    "set_memory_service"
]
