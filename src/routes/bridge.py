from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..services import MemoryService
from .dependencies import get_memory_service

router = APIRouter()

class BridgeRequest(BaseModel):
    """Request model for creating cross-session bridges."""
    source_session: str
    target_session: str
    shared_context: List[str]

class BridgeResponse(BaseModel):
    """Response model for cross-session bridge."""
    id: str
    source_session: str
    target_session: str
    shared_context: List[str]
    strength: float
    metadata: dict

@router.post("/bridge", response_model=BridgeResponse)
async def create_cross_session_bridge(
    request: BridgeRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Create a bridge between two memory sessions."""
    # Create a memory that represents the bridge
    bridge_content = f"Connection between sessions {request.source_session} and {request.target_session}: {', '.join(request.shared_context)}"
    
    result = await memory_service.add_memory(
        messages=[{
            "content": bridge_content,
            "role": "system"
        }],
        metadata={
            "type": "bridge",
            "source_session": request.source_session,
            "target_session": request.target_session,
            "shared_context": request.shared_context
        }
    )

    # Calculate bridge strength based on context overlap
    # This is a simple implementation - could be made more sophisticated
    strength = min(1.0, len(request.shared_context) * 0.2)

    return BridgeResponse(
        id=result["id"],
        source_session=request.source_session,
        target_session=request.target_session,
        shared_context=request.shared_context,
        strength=strength,
        metadata=result.get("metadata", {})
    )

@router.get("/bridge/{session_id}", response_model=List[BridgeResponse])
async def get_session_bridges(
    session_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get all bridges connected to a session."""
    results = await memory_service.search_memories(
        query="",
        filters={
            "type": "bridge",
            "$or": [
                {"source_session": session_id},
                {"target_session": session_id}
            ]
        }
    )

    bridges = []
    for result in results:
        metadata = result.get("metadata", {})
        bridges.append(BridgeResponse(
            id=result["id"],
            source_session=metadata.get("source_session"),
            target_session=metadata.get("target_session"),
            shared_context=metadata.get("shared_context", []),
            strength=min(1.0, len(metadata.get("shared_context", [])) * 0.2),
            metadata=metadata
        ))

    return bridges
