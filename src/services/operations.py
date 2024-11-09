"""Service for memory operations."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import pytz
from ..utils.logging import LoggerMixin
from .base import BaseMemoryService

class MemoryOperations(LoggerMixin):
    """Service for handling memory operations."""

    def __init__(self):
        """Initialize operations service."""
        super().__init__()
        self.base_service = BaseMemoryService()

    async def add_memory(
        self,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a new memory."""
        try:
            # Add timestamp to metadata
            metadata = metadata or {}
            metadata["created_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()
            
            result = await self.base_service.add_memory(
                messages=messages,
                metadata=metadata
            )
            
            self.log_info(
                "Memory added",
                result=result
            )
            
            return result
        
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
            # Get existing memory
            memory = await self.base_service.get_memory_by_id(memory_id)
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            # Add update timestamp
            if "metadata" not in updates:
                updates["metadata"] = {}
            updates["metadata"]["updated_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()
            
            # Preserve existing metadata
            if "metadata" in memory:
                updates["metadata"].update({
                    k: v for k, v in memory["metadata"].items()
                    if k not in updates["metadata"]
                })
            
            result = await self.base_service.update_memory(
                memory_id=memory_id,
                updates=updates
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

    async def delete_memory(
        self,
        memory_id: str
    ) -> bool:
        """Delete a memory."""
        try:
            # Get existing memory
            memory = await self.base_service.get_memory_by_id(memory_id)
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            # Mark memory as deleted
            await self.base_service.update_memory(
                memory_id=memory_id,
                updates={
                    "metadata": {
                        **memory.get("metadata", {}),
                        "deleted": True,
                        "deleted_at": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                    }
                }
            )
            
            self.log_info(
                "Memory deleted",
                memory_id=memory_id
            )
            
            return True
        
        except Exception as e:
            self.log_error(
                "Failed to delete memory",
                error=str(e),
                memory_id=memory_id,
                exc_info=True
            )
            raise

    async def batch_update_memories(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update multiple memories in batch."""
        results = []
        errors = []
        
        for update in updates:
            try:
                memory_id = update.get("id")
                if not memory_id:
                    raise ValueError("Memory ID is required")
                
                result = await self.update_memory(
                    memory_id=memory_id,
                    updates=update.get("updates", {})
                )
                results.append(result)
            
            except Exception as e:
                self.log_error(
                    "Failed to update memory in batch",
                    error=str(e),
                    update=update,
                    exc_info=True
                )
                errors.append({
                    "id": update.get("id"),
                    "error": str(e)
                })
        
        if errors:
            self.log_warning(
                "Some batch updates failed",
                error_count=len(errors),
                success_count=len(results)
            )
        
        return {
            "results": results,
            "errors": errors
        }
