"""Memory service implementation."""
from typing import Dict, List, Any, Optional
import logging
from mem0 import Memory
from src.models import MemoryServiceProtocol
from src.config import settings

logger = logging.getLogger(__name__)

class MemoryService(MemoryServiceProtocol):
    """Memory service implementation."""

    def __init__(self):
        """Initialize memory service."""
        self.logger = logger.getChild("memory_service")
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
            
            result = self.memory.add(
                messages=messages,
                user_id=filters.get("user_id"),
                agent_id=filters.get("agent_id"),
                run_id=filters.get("run_id"),
                filters=filters
            )
            
            self.logger.info("Memory added: %s", result)
            
            return result.get("results", [])[0] if result.get("results") else {}
        
        except Exception as e:
            self.logger.error(
                "Failed to add memory: %s, messages=%s, metadata=%s",
                str(e),
                messages,
                metadata,
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
            result = self.memory.update(
                memory_id=memory_id,
                data=updates.get("content", "")
            )
            
            self.logger.info(
                "Memory updated: memory_id=%s, updates=%s",
                memory_id,
                updates
            )
            
            return result
        
        except Exception as e:
            self.logger.error(
                "Failed to update memory: %s, memory_id=%s, updates=%s",
                str(e),
                memory_id,
                updates,
                exc_info=True
            )
            raise

    async def get_memory_by_id(
        self,
        memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        try:
            result = self.memory.get(memory_id)
            
            if result:
                self.logger.debug(
                    "Memory retrieved: memory_id=%s",
                    memory_id
                )
            else:
                self.logger.warning(
                    "Memory not found: memory_id=%s",
                    memory_id
                )
            
            return result
        
        except Exception as e:
            self.logger.error(
                "Failed to get memory: %s, memory_id=%s",
                str(e),
                memory_id,
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
            result = self.memory.search(
                query=query,
                user_id=filters.get("user_id") if filters else None,
                agent_id=filters.get("agent_id") if filters else None,
                run_id=filters.get("run_id") if filters else None,
                filters=filters,
                limit=limit
            )
            
            self.logger.info(
                "Memory search completed: query=%s, filters=%s, limit=%d, result_count=%d",
                query,
                filters,
                limit,
                len(result.get("results", []))
            )
            
            return result.get("results", [])
        
        except Exception as e:
            self.logger.error(
                "Failed to search memories: %s, query=%s, filters=%s, limit=%d",
                str(e),
                query,
                filters,
                limit,
                exc_info=True
            )
            raise

    async def get_memory_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get memory history."""
        try:
            history = self.memory.history(memory_id)
            
            self.logger.info(
                "Memory history retrieved: memory_id=%s, history_count=%d",
                memory_id,
                len(history)
            )
            
            return history
        
        except Exception as e:
            self.logger.error(
                "Failed to get memory history: %s, memory_id=%s",
                str(e),
                memory_id,
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
            result = self.memory.search(
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
            
            self.logger.info(
                "Memory relations retrieved: memory_id=%s, relation_count=%d",
                memory_id,
                len(relations)
            )
            
            return relations
        
        except Exception as e:
            self.logger.error(
                "Failed to get memory relations: %s, memory_id=%s",
                str(e),
                memory_id,
                exc_info=True
            )
            raise

    async def cleanup(self):
        """Clean up resources."""
        try:
            # Reset collections
            self.memory.reset()
            
            self.logger.info("Memory service cleaned up")
        
        except Exception as e:
            self.logger.error(
                "Failed to cleanup memory service: %s",
                str(e),
                exc_info=True
            )
            raise
