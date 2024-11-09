"""Suggestion routes for memory system."""
from fastapi import APIRouter, Depends
from src.dependencies import get_memory_service
from src.models import MemoryServiceProtocol

router = APIRouter()

@router.get("/{memory_id}")
async def get_suggestions(
    memory_id: str,
    limit: int = 10,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Get suggestions for a memory."""
    memory = await memory_service.get_memory_by_id(memory_id)
    if not memory:
        return []
    
    # Search for similar memories
    suggestions = await memory_service.search_memories(
        query=memory.get("content", ""),
        filters={
            "type": "suggestion",
            "memory_id": memory_id
        },
        limit=limit
    )
    
    return suggestions
