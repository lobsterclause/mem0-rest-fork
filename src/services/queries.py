"""Service for memory queries and searches."""
from typing import Dict, List, Any, Optional
from ..utils.logging import LoggerMixin
from .base import BaseMemoryService

class MemoryQueries(LoggerMixin):
    """Service for handling memory queries and searches."""

    def __init__(self):
        """Initialize queries service."""
        super().__init__()
        self.base_service = BaseMemoryService()

    async def search_memories(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search memories with pagination."""
        try:
            # Apply pagination to search
            search_limit = limit + 1  # Get one extra to check if there are more results
            results = await self.base_service.search_memories(
                query=query,
                filters=filters,
                limit=search_limit
            )
            
            # Check if there are more results
            has_more = len(results) > limit
            if has_more:
                results = results[:limit]
            
            response = {
                "results": results,
                "total": len(results),
                "page": offset // limit + 1,
                "pageSize": limit,
                "hasMore": has_more,
                "filters": filters or {}
            }
            
            self.log_info(
                "Memory search completed",
                query=query,
                filters=filters,
                limit=limit,
                offset=offset,
                result_count=len(results)
            )
            
            return response
        
        except Exception as e:
            self.log_error(
                "Failed to search memories",
                error=str(e),
                query=query,
                filters=filters,
                limit=limit,
                offset=offset,
                exc_info=True
            )
            raise

    async def get_suggestions(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get memory suggestions based on query."""
        try:
            # Search with minimal content to get suggestions
            results = await self.base_service.search_memories(
                query=query,
                filters=filters,
                limit=limit
            )
            
            # Extract relevant suggestion data
            suggestions = [{
                "id": result["id"],
                "content": result.get("memory", result.get("content", "")),
                "type": result.get("metadata", {}).get("type", "memory"),
                "score": result.get("score", 0.0)
            } for result in results]
            
            self.log_info(
                "Memory suggestions retrieved",
                query=query,
                limit=limit,
                filters=filters,
                suggestion_count=len(suggestions)
            )
            
            return suggestions
        
        except Exception as e:
            self.log_error(
                "Failed to get memory suggestions",
                error=str(e),
                query=query,
                limit=limit,
                filters=filters,
                exc_info=True
            )
            raise

    async def get_similar_memories(
        self,
        memory_id: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get memories similar to the given memory."""
        try:
            # Get the source memory
            memory = await self.base_service.get_memory_by_id(memory_id)
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            # Use memory content as query
            content = memory.get("memory", memory.get("content", ""))
            if not content:
                raise ValueError(f"Memory {memory_id} has no content")
            
            # Combine filters
            search_filters = filters or {}
            search_filters.update({
                "id": {"$ne": memory_id}  # Exclude the source memory
            })
            
            # Search using memory content
            results = await self.base_service.search_memories(
                query=content,
                filters=search_filters,
                limit=limit
            )
            
            self.log_info(
                "Similar memories retrieved",
                memory_id=memory_id,
                limit=limit,
                filters=filters,
                similar_count=len(results)
            )
            
            return results
        
        except Exception as e:
            self.log_error(
                "Failed to get similar memories",
                error=str(e),
                memory_id=memory_id,
                limit=limit,
                filters=filters,
                exc_info=True
            )
            raise

    async def get_memory_by_id(
        self,
        memory_id: str,
        include_similar: bool = False,
        similar_limit: int = 5
    ) -> Dict[str, Any]:
        """Get a memory by ID with optional similar memories."""
        try:
            # Get the memory
            memory = await self.base_service.get_memory_by_id(memory_id)
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            # Get similar memories if requested
            if include_similar:
                similar = await self.get_similar_memories(
                    memory_id=memory_id,
                    limit=similar_limit
                )
                memory["similar"] = similar
            
            self.log_info(
                "Memory retrieved",
                memory_id=memory_id,
                include_similar=include_similar
            )
            
            return memory
        
        except Exception as e:
            self.log_error(
                "Failed to get memory",
                error=str(e),
                memory_id=memory_id,
                include_similar=include_similar,
                exc_info=True
            )
            raise
