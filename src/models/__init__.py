"""Models package for memory system."""
from typing import List, Dict, Any, Optional, Protocol
from pydantic import BaseModel

class Message(BaseModel):
    """Message model."""
    role: str
    content: str

class MemoryCreateRequest(BaseModel):
    """Request model for creating a memory."""
    messages: List[Message]
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    run_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None

class MemoryUpdateRequest(BaseModel):
    """Request model for updating a memory."""
    messages: List[Message]
    user_id: Optional[str] = None
    agent_id: Optional[str] = None

class SessionMemory(BaseModel):
    """Session memory model."""
    id: str
    content: str
    metadata: Dict[str, Any]

class CrossSessionBridge(BaseModel):
    """Cross-session bridge model."""
    source_id: str
    target_id: str
    relation_type: str
    metadata: Dict[str, Any]

class MemoryServiceProtocol(Protocol):
    """Protocol defining memory service interface."""

    async def add_memory(
        self,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a new memory."""
        ...

    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing memory."""
        ...

    async def get_memory_by_id(
        self,
        memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        ...

    async def search_memories(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories."""
        ...

    async def get_memory_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get memory history."""
        ...

    async def get_memory_relations(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get memory relations."""
        ...
