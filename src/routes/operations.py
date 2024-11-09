"""Operations routes."""
from fastapi import APIRouter, Depends
from src.dependencies import get_memory_service
from src.services.types import MemoryServiceProtocol
from src.routes.models import MemoryCreateRequest, MemoryUpdateRequest

router = APIRouter()

@router.post("/")
async def add_memory(
    request: MemoryCreateRequest,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Add a new memory."""
    return await memory_service.add_memory(
        messages=[msg.dict() for msg in request.messages],
        metadata={
            "user_id": request.user_id,
            "agent_id": request.agent_id,
            "run_id": request.run_id,
            "filters": request.filters,
            "prompt": request.prompt
        }
    )

@router.put("/{memory_id}")
async def update_memory(
    memory_id: str,
    request: MemoryUpdateRequest,
    memory_service: MemoryServiceProtocol = Depends(get_memory_service)
):
    """Update an existing memory."""
    return await memory_service.update_memory(
        memory_id=memory_id,
        updates={
            "messages": [msg.dict() for msg in request.messages],
            "metadata": {
                "user_id": request.user_id,
                "agent_id": request.agent_id
            }
        }
    )
