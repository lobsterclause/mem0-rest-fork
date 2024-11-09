"""Service for memory history and relations."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import pytz
from ..utils.logging import LoggerMixin
from .base import BaseMemoryService

class MemoryHistory(LoggerMixin):
    """Service for handling memory history and relations."""

    def __init__(self):
        """Initialize history service."""
        super().__init__()
        self.base_service = BaseMemoryService()

    async def get_memory_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get history of changes for a memory."""
        try:
            history = await self.base_service.get_memory_history(memory_id)
            
            # Sort history by timestamp
            history.sort(
                key=lambda x: datetime.fromisoformat(
                    x.get("timestamp", "1970-01-01T00:00:00")
                ),
                reverse=True
            )
            
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
        memory_id: str,
        relation_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get relations for a memory."""
        try:
            relations = await self.base_service.get_memory_relations(memory_id)
            
            # Filter by relation types if specified
            if relation_types:
                relations = [
                    r for r in relations
                    if r.get("type") in relation_types
                ]
            
            # Group relations by type
            grouped_relations: Dict[str, List[Dict[str, Any]]] = {}
            for relation in relations:
                rel_type = relation.get("type", "unknown")
                if rel_type not in grouped_relations:
                    grouped_relations[rel_type] = []
                grouped_relations[rel_type].append(relation)
            
            self.log_info(
                "Memory relations retrieved",
                memory_id=memory_id,
                relation_count=len(relations),
                relation_types=list(grouped_relations.keys())
            )
            
            return grouped_relations
        
        except Exception as e:
            self.log_error(
                "Failed to get memory relations",
                error=str(e),
                memory_id=memory_id,
                relation_types=relation_types,
                exc_info=True
            )
            raise

    async def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a relation between two memories."""
        try:
            # Validate memories exist
            source = await self.base_service.get_memory_by_id(source_id)
            target = await self.base_service.get_memory_by_id(target_id)
            
            if not source:
                raise ValueError(f"Source memory {source_id} not found")
            if not target:
                raise ValueError(f"Target memory {target_id} not found")
            
            # Create relation metadata
            relation_metadata = {
                "type": relation_type,
                "source_id": source_id,
                "target_id": target_id,
                "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat(),
                **(metadata or {})
            }
            
            # Add relation memory
            relation = await self.base_service.add_memory(
                messages=[{
                    "content": f"Relation {relation_type} from {source_id} to {target_id}",
                    "role": "system"
                }],
                metadata=relation_metadata
            )
            
            self.log_info(
                "Memory relation added",
                relation_id=relation.get("id"),
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type
            )
            
            return relation
        
        except Exception as e:
            self.log_error(
                "Failed to add memory relation",
                error=str(e),
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                metadata=metadata,
                exc_info=True
            )
            raise

    async def remove_relation(
        self,
        relation_id: str
    ) -> bool:
        """Remove a relation between memories."""
        try:
            # Get relation memory
            relation = await self.base_service.get_memory_by_id(relation_id)
            if not relation:
                raise ValueError(f"Relation {relation_id} not found")
            
            # Mark relation as deleted
            await self.base_service.update_memory(
                memory_id=relation_id,
                updates={
                    "metadata": {
                        **relation.get("metadata", {}),
                        "deleted": True,
                        "deleted_at": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                    }
                }
            )
            
            self.log_info(
                "Memory relation removed",
                relation_id=relation_id
            )
            
            return True
        
        except Exception as e:
            self.log_error(
                "Failed to remove memory relation",
                error=str(e),
                relation_id=relation_id,
                exc_info=True
            )
            raise

    async def get_relation_history(
        self,
        source_id: str,
        target_id: str,
        relation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get history of relations between two memories."""
        try:
            # Search for relation history
            filters = {
                "$or": [
                    {"source_id": source_id, "target_id": target_id},
                    {"source_id": target_id, "target_id": source_id}
                ],
                "type": "relation"
            }
            if relation_type:
                filters["relation_type"] = relation_type
            
            relations = await self.base_service.search_memories(
                query="",
                filters=filters
            )
            
            # Sort by timestamp
            relations.sort(
                key=lambda x: datetime.fromisoformat(
                    x.get("metadata", {}).get("timestamp", "1970-01-01T00:00:00")
                ),
                reverse=True
            )
            
            self.log_info(
                "Relation history retrieved",
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                history_count=len(relations)
            )
            
            return relations
        
        except Exception as e:
            self.log_error(
                "Failed to get relation history",
                error=str(e),
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                exc_info=True
            )
            raise
