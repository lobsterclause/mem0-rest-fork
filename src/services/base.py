"""Base memory service implementation."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import pytz
from mem0 import Memory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config import settings
from src.utils.logging import LoggerMixin

class BaseMemoryService(LoggerMixin):
    """Base service for memory operations."""

    def __init__(self):
        """Initialize base memory service."""
        super().__init__()
        self.memory = Memory(settings.to_mem0_config())

    async def add_memory(
        self,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a new memory."""
        try:
            # Extract user/agent/run IDs from metadata
            filters = {}
            if metadata:
                for key in ["user_id", "agent_id", "run_id"]:
                    if key in metadata:
                        filters[key] = metadata[key]
            
            result = await self.memory.add(
                messages=messages,
                user_id=filters.get("user_id"),
                agent_id=filters.get("agent_id"),
                run_id=filters.get("run_id"),
                filters=filters
            )
            
            self.log_info(
                "Memory added",
                result=result
            )
            
            return result.get("results", [])[0] if result.get("results") else {}
        
        except Exception as e:
            self.log_error(
                "Failed to add memory",
                error=str(e),
                messages=messages,
                metadata=metadata,
                exc_info=True
            )
            raise

    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing memory."""
        try:
            # Add update timestamp
            if "metadata" in updates:
                updates["metadata"]["updated_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()
            
            result = await self.memory.update(
                memory_id=memory_id,
                data=updates.get("content", "")
            )
            
            self.log_info(
                "Memory updated",
                memory_id=memory_id,
                updates=updates
            )
            
            return result
        
        except Exception as e:
            self.log_error(
                "Failed to update memory",
                error=str(e),
                memory_id=memory_id,
                updates=updates,
                exc_info=True
            )
            raise

    async def get_memory_by_id(
        self,
        memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        try:
            result = await self.memory.get(memory_id)
            
            if result:
                self.log_debug(
                    "Memory retrieved",
                    memory_id=memory_id
                )
            else:
                self.log_warning(
                    "Memory not found",
                    memory_id=memory_id
                )
            
            return result
        
        except Exception as e:
            self.log_error(
                "Failed to get memory",
                error=str(e),
                memory_id=memory_id,
                exc_info=True
            )
            raise

    async def search_memories(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories."""
        try:
            result = await self.memory.search(
                query=query,
                user_id=filters.get("user_id") if filters else None,
                agent_id=filters.get("agent_id") if filters else None,
                run_id=filters.get("run_id") if filters else None,
                filters=filters,
                limit=limit
            )
            
            self.log_info(
                "Memory search completed",
                query=query,
                filters=filters,
                limit=limit,
                result_count=len(result.get("results", []))
            )
            
            return result.get("results", [])
        
        except Exception as e:
            self.log_error(
                "Failed to search memories",
                error=str(e),
                query=query,
                filters=filters,
                limit=limit,
                exc_info=True
            )
            raise

    async def get_memory_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get memory history."""
        try:
            history = await self.memory.history(memory_id)
            
            self.log_info(
                "Memory history retrieved",
                memory_id=memory_id,
                history_count=len(history)
            )
            
            return history
        
        except Exception as e:
            self.log_error(
                "Failed to get memory history",
                error=str(e),
                memory_id=memory_id,
                exc_info=True
            )
            raise

    async def get_memory_relations(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get memory relations."""
        try:
            # Search for relations using metadata
            result = await self.memory.search(
                query="",
                filters={
                    "$or": [
                        {"source_id": memory_id},
                        {"target_id": memory_id}
                    ],
                    "type": "relation"
                }
            )
            
            relations = result.get("relations", [])
            
            self.log_info(
                "Memory relations retrieved",
                memory_id=memory_id,
                relation_count=len(relations)
            )
            
            return relations
        
        except Exception as e:
            self.log_error(
                "Failed to get memory relations",
                error=str(e),
                memory_id=memory_id,
                exc_info=True
            )
            raise

    async def cleanup(self):
        """Clean up resources."""
        try:
            # Reset collections
            await self.memory.reset()
            
            self.log_info("Memory service cleaned up")
        
        except Exception as e:
            self.log_error(
                "Failed to cleanup memory service",
                error=str(e),
                exc_info=True
            )
            raise
