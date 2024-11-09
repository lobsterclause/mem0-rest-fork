"""History routes for memory system."""
from fastapi import APIRouter, Depends
from src.dependencies import get_memory_service
from src.models import MemoryServiceProtocol

router = APIRouter()

@router.get("/{memory_id}")
async def get_memory_history(
    memory_id: str,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Get memory history."""
    return await memory_service.get_memory_history(memory_id)

@router.get("/{memory_id}/relations")
async def get_memory_relations(
    memory_id: str,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Get memory relations."""
    return await memory_service.get_memory_relations(memory_id)
