"""Session management service."""
import logging
from src.models import SessionMemory, CrossSessionBridge, MemoryServiceProtocol

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing session-based memory operations."""

    def __init__(self, memory_service: MemoryServiceProtocol):
        """Initialize session service."""
        self.memory_service = memory_service
        self.logger = logger.getChild("session_service")

    async def create_session(self, user_id: str) -> SessionMemory:
        """Create a new session."""
        try:
            # Create session memory
            session = SessionMemory(user_id=user_id)
            
            self.logger.info(
                "Session created: user_id=%s, session_id=%s",
                user_id,
                session.session_id
            )
            
            return session
        
        except Exception as e:
            self.logger.error(
                "Failed to create session: %s, user_id=%s",
                str(e),
                user_id,
                exc_info=True
            )
            raise

    async def get_session(self, session_id: str) -> SessionMemory:
        """Get session by ID."""
        try:
            # Get session memory
            session = await self.memory_service.get_memory_by_id(session_id)
            
            if session:
                self.logger.debug(
                    "Session retrieved: session_id=%s",
                    session_id
                )
            else:
                self.logger.warning(
                    "Session not found: session_id=%s",
                    session_id
                )
            
            return session
        
        except Exception as e:
            self.logger.error(
                "Failed to get session: %s, session_id=%s",
                str(e),
                session_id,
                exc_info=True
            )
            raise

    async def update_session(
        self,
        session_id: str,
        updates: dict
    ) -> SessionMemory:
        """Update session."""
        try:
            # Update session memory
            session = await self.memory_service.update_memory(
                memory_id=session_id,
                updates=updates
            )
            
            self.logger.info(
                "Session updated: session_id=%s, updates=%s",
                session_id,
                updates
            )
            
            return session
        
        except Exception as e:
            self.logger.error(
                "Failed to update session: %s, session_id=%s, updates=%s",
                str(e),
                session_id,
                updates,
                exc_info=True
            )
            raise

    async def delete_session(self, session_id: str):
        """Delete session."""
        try:
            # Delete session memory
            await self.memory_service.cleanup()
            
            self.logger.info(
                "Session deleted: session_id=%s",
                session_id
            )
        
        except Exception as e:
            self.logger.error(
                "Failed to delete session: %s, session_id=%s",
                str(e),
                session_id,
                exc_info=True
            )
            raise

    async def create_bridge(
        self,
        source_id: str,
        target_id: str,
        bridge_type: str
    ) -> CrossSessionBridge:
        """Create cross-session bridge."""
        try:
            # Create bridge
            bridge = CrossSessionBridge(
                source_id=source_id,
                target_id=target_id,
                bridge_type=bridge_type
            )
            
            self.logger.info(
                "Bridge created: source_id=%s, target_id=%s, type=%s",
                source_id,
                target_id,
                bridge_type
            )
            
            return bridge
        
        except Exception as e:
            self.logger.error(
                "Failed to create bridge: %s, source_id=%s, target_id=%s, type=%s",
                str(e),
                source_id,
                target_id,
                bridge_type,
                exc_info=True
            )
            raise

    async def get_bridges(
        self,
        session_id: str
    ) -> list[CrossSessionBridge]:
        """Get bridges for session."""
        try:
            # Get bridges
            bridges = await self.memory_service.get_memory_relations(session_id)
            
            self.logger.info(
                "Bridges retrieved: session_id=%s, count=%d",
                session_id,
                len(bridges)
            )
            
            return bridges
        
        except Exception as e:
            self.logger.error(
                "Failed to get bridges: %s, session_id=%s",
                str(e),
                session_id,
                exc_info=True
            )
            raise
