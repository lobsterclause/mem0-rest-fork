"""Query routes for memory system."""
from fastapi import APIRouter, Depends
from src.dependencies import get_memory_service
from src.models import MemoryServiceProtocol

router = APIRouter()

@router.get("/{memory_id}")
async def get_memory(
    memory_id: str,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Get a memory by ID."""
    return await memory_service.get_memory_by_id(memory_id)

@router.get("/")
async def search_memories(
    query: str,
    user_id: str = None,
    agent_id: str = None,
    run_id: str = None,
    limit: int = 10,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Search memories."""
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if agent_id:
        filters["agent_id"] = agent_id
    if run_id:
        filters["run_id"] = run_id
    
    return await memory_service.search_memories(
        query=query,
        filters=filters,
        limit=limit
    )
