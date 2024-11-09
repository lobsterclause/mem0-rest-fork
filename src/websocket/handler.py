"""WebSocket handler for memory system."""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import pytz
from fastapi import WebSocket, WebSocketDisconnect
from ..utils.logging import LoggerMixin
from ..services.streaming import streaming_service

class WebSocketHandler(LoggerMixin):
    """Handler for WebSocket connections."""

    def __init__(self):
        """Initialize WebSocket handler."""
        super().__init__()
        self.streaming = streaming_service

    async def handle_connection(
        self,
        websocket: WebSocket,
        user_id: str,
        session_id: str
    ):
        """Handle a WebSocket connection."""
        try:
            # Accept connection
            await self.streaming.connect(
                websocket=websocket,
                user_id=user_id,
                session_id=session_id
            )
            
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection_established",
                "data": {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            })
            
            try:
                # Handle messages
                await self.handle_messages(
                    websocket=websocket,
                    user_id=user_id,
                    session_id=session_id
                )
            
            except WebSocketDisconnect:
                self.log_info(
                    "WebSocket client disconnected",
                    user_id=user_id,
                    session_id=session_id
                )
            
            finally:
                # Clean up connection
                await self.streaming.disconnect(
                    user_id=user_id,
                    session_id=session_id
                )
        
        except Exception as e:
            self.log_error(
                "Error handling WebSocket connection",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                exc_info=True
            )
            raise

    async def handle_messages(
        self,
        websocket: WebSocket,
        user_id: str,
        session_id: str
    ):
        """Handle WebSocket messages."""
        try:
            while True:
                # Get message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle message based on type
                message_type = message.get("type")
                
                if message_type == "memory_update":
                    await self.handle_memory_update(
                        websocket=websocket,
                        user_id=user_id,
                        session_id=session_id,
                        data=message.get("data", {})
                    )
                
                elif message_type == "ping":
                    await self.handle_ping(
                        websocket=websocket,
                        timestamp=message.get("timestamp")
                    )
                
                else:
                    self.log_warning(
                        "Unknown message type",
                        message_type=message_type,
                        user_id=user_id,
                        session_id=session_id
                    )
        
        except WebSocketDisconnect:
            raise
        
        except Exception as e:
            self.log_error(
                "Error handling WebSocket messages",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                exc_info=True
            )
            raise

    async def handle_memory_update(
        self,
        websocket: WebSocket,
        user_id: str,
        session_id: str,
        data: Dict[str, Any]
    ):
        """Handle memory update message."""
        try:
            # Broadcast update to other connections
            await self.streaming.broadcast_to_user(
                user_id=user_id,
                message_type="memory_update",
                data=data,
                exclude=session_id
            )
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "memory_update_ack",
                "data": {
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            })
        
        except Exception as e:
            self.log_error(
                "Error handling memory update",
                error=str(e),
                user_id=user_id,
                session_id=session_id,
                data=data,
                exc_info=True
            )
            # Send error response
            await websocket.send_json({
                "type": "error",
                "data": {
                    "message": str(e),
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            })

    async def handle_ping(
        self,
        websocket: WebSocket,
        timestamp: Optional[str] = None
    ):
        """Handle ping message."""
        try:
            await websocket.send_json({
                "type": "pong",
                "data": {
                    "timestamp": timestamp or datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            })
        
        except Exception as e:
            self.log_error(
                "Error handling ping",
                error=str(e),
                timestamp=timestamp,
                exc_info=True
            )

    async def broadcast_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Broadcast event to all connections or specific user."""
        try:
            if user_id:
                await self.streaming.broadcast_to_user(
                    user_id=user_id,
                    message_type=event_type,
                    data=data
                )
            else:
                # Broadcast to all users
                for uid in self.streaming.active_connections:
                    await self.streaming.broadcast_to_user(
                        user_id=uid,
                        message_type=event_type,
                        data=data
                    )
        
        except Exception as e:
            self.log_error(
                "Error broadcasting event",
                error=str(e),
                event_type=event_type,
                data=data,
                user_id=user_id,
                exc_info=True
            )

# Global WebSocket handler instance
ws_handler = WebSocketHandler()
