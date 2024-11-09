"""Compression routes for memory system."""
from fastapi import APIRouter, Depends
from src.dependencies import get_memory_service
from src.models import MemoryServiceProtocol

router = APIRouter()

@router.post("/{memory_id}")
async def compress_memory(
    memory_id: str,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Compress a memory."""
    memory = await memory_service.get_memory_by_id(memory_id)
    if not memory:
        return {"error": "Memory not found"}
    
    # Get related memories
    relations = await memory_service.get_memory_relations(memory_id)
    
    # Combine memory content with related memories
    combined_content = memory.get("content", "")
    for relation in relations:
        related_memory = await memory_service.get_memory_by_id(
            relation.get("target_id")
            if relation.get("source_id") == memory_id
            else relation.get("source_id")
        )
        if related_memory:
            combined_content += "\n" + related_memory.get("content", "")
    
    # Create compressed memory
    compressed = await memory_service.add_memory(
        messages=[],
        metadata={
            "type": "compressed",
            "original_id": memory_id,
            "content": combined_content
        }
    )
    
    return compressed
