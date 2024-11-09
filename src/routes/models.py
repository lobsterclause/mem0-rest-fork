"""Models for memory routes."""
from typing import List, Dict, Any, Optional
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
