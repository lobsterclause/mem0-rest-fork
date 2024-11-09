"""Service for handling memory streaming."""
from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
import json
from datetime import datetime
import pytz
from fastapi import WebSocket
from ..utils.logging import LoggerMixin

class StreamingService(LoggerMixin):
    """Service for handling memory streaming."""

    def __init__(self):
        """Initialize streaming service."""
        super().__init__()
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        session_id: str
    ):
        """Connect a new WebSocket client."""
        try:
            await websocket.accept()
            
            if user_id not in self.active_connections:
                self.active_connections[user_id] = {}
            self.active_connections[user_id][session_id] = websocket
            
            self.log_info(
                "WebSocket client connected",
                user_id=user_id,
                session_id=session_id
            )
        
        except Exception as e:
            self.log_error(
                "Failed to connect WebSocket client",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                exc_info=True
            )
            raise

    async def disconnect(
        self,
        user_id: str,
        session_id: str
    ):
        """Disconnect a WebSocket client."""
        try:
            if user_id in self.active_connections:
                if session_id in self.active_connections[user_id]:
                    del self.active_connections[user_id][session_id]
                    if not self.active_connections[user_id]:
                        del self.active_connections[user_id]
            
            self.log_info(
                "WebSocket client disconnected",
                user_id=user_id,
                session_id=session_id
            )
        
        except Exception as e:
            self.log_error(
                "Failed to disconnect WebSocket client",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                exc_info=True
            )

    async def broadcast_to_user(
        self,
        user_id: str,
        message_type: str,
        data: Dict[str, Any],
        exclude: Optional[str] = None
    ):
        """Broadcast message to all user's connections."""
        if user_id not in self.active_connections:
            return
        
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
        }
        
        for session_id, websocket in self.active_connections[user_id].items():
            if exclude and session_id == exclude:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                self.log_error(
                    "Failed to send message to WebSocket client",
                    error=str(e),
                    user_id=user_id,
                    session_id=session_id,
                    message_type=message_type,
                    exc_info=True
                )

    async def stream_memory_chunks(
        self,
        user_id: str,
        session_id: str,
        content: str,
        chunk_size: int = 100
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream memory content in chunks."""
        try:
            # Split content into chunks
            chunks = [
                content[i:i + chunk_size]
                for i in range(0, len(content), chunk_size)
            ]
            
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(chunks):
                # Create chunk data
                chunk_data = {
                    "id": f"{session_id}_{i}",
                    "content": chunk,
                    "type": "memory_chunk",
                    "done": i == total_chunks - 1,
                    "metadata": {
                        "chunk_number": i + 1,
                        "total_chunks": total_chunks,
                        "session_id": session_id,
                        "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                    }
                }
                
                # Broadcast chunk to all user's connections
                await self.broadcast_to_user(
                    user_id=user_id,
                    message_type="memory_chunk",
                    data=chunk_data
                )
                
                # Yield chunk for direct API response
                yield chunk_data
                
                # Small delay between chunks
                await asyncio.sleep(0.05)

        except Exception as e:
            self.log_error(
                "Error streaming memory chunks",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                exc_info=True
            )
            # Send error notification
            error_data = {
                "id": f"{session_id}_error",
                "type": "error",
                "content": str(e),
                "done": True,
                "metadata": {
                    "session_id": session_id,
                    "error": True,
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            }
            await self.broadcast_to_user(
                user_id=user_id,
                message_type="memory_error",
                data=error_data
            )
            yield error_data

    async def stream_memory_updates(
        self,
        websocket: WebSocket,
        user_id: str,
        session_id: str
    ):
        """Stream memory updates over WebSocket."""
        try:
            while True:
                # Wait for message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "memory_update":
                    # Broadcast update to other connections
                    await self.broadcast_to_user(
                        user_id=user_id,
                        message_type="memory_update",
                        data=message.get("data", {}),
                        exclude=session_id
                    )
                    
                    # Send acknowledgment
                    await websocket.send_json({
                        "type": "memory_update_ack",
                        "data": {
                            "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                        }
                    })
                
                elif message.get("type") == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })

        except Exception as e:
            self.log_error(
                "Error in memory update stream",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                exc_info=True
            )
            # Let the WebSocket handler deal with the error
            raise

# Global streaming service instance
streaming_service = StreamingService()
