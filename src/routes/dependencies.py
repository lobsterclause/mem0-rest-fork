"""Dependencies for routes."""
from fastapi import Depends
from src.dependencies import get_memory_service as get_memory_service_dependency
from src.models import MemoryServiceProtocol

async def get_memory_service() -> MemoryServiceProtocol:
    """Get memory service dependency."""
    return await get_memory_service_dependency()
