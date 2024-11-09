"""Type definitions for services."""
from typing import Protocol, Dict, List, Any, Optional

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
