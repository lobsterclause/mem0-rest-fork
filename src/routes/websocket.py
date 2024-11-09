"""WebSocket routes for memory system."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from ..middleware.auth import get_websocket_user
from ..middleware.rate_limit import check_ws_rate_limit
from ..websocket.handler import ws_handler
from ..utils.logging import LoggerMixin

router = APIRouter()
logger = LoggerMixin()

@router.websocket("/memory/{session_id}")
async def memory_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for memory updates."""
    try:
        # Authenticate WebSocket connection
        user = await get_websocket_user(websocket)
        
        # Check rate limit
        if not await check_ws_rate_limit(websocket, user.get("id")):
            await websocket.close(code=1008)  # Policy Violation
            return
        
        # Handle connection
        await ws_handler.handle_connection(
            websocket=websocket,
            user_id=user.get("id"),
            session_id=session_id
        )
    
    except WebSocketDisconnect:
        logger.log_info(
            "WebSocket client disconnected",
            session_id=session_id
        )
    except Exception as e:
        logger.log_error(
            "Error in memory WebSocket",
            error=str(e),
            session_id=session_id,
            exc_info=True
        )
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011)  # Internal Error

@router.websocket("/stream/{session_id}")
async def stream_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming memory content."""
    try:
        # Authenticate WebSocket connection
        user = await get_websocket_user(websocket)
        
        # Check rate limit
        if not await check_ws_rate_limit(websocket, user.get("id")):
            await websocket.close(code=1008)  # Policy Violation
            return
        
        # Accept connection
        await websocket.accept()
        
        # Handle streaming
        await ws_handler.streaming.stream_memory_updates(
            websocket=websocket,
            user_id=user.get("id"),
            session_id=session_id
        )
    
    except WebSocketDisconnect:
        logger.log_info(
            "Stream client disconnected",
            session_id=session_id
        )
    except Exception as e:
        logger.log_error(
            "Error in stream WebSocket",
            error=str(e),
            session_id=session_id,
            exc_info=True
        )
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011)  # Internal Error

@router.post("/broadcast/{event_type}")
async def broadcast_event(
    event_type: str,
    data: dict,
    user_id: str = None,
    current_user: dict = Depends(get_websocket_user)
):
    """Broadcast event to WebSocket clients."""
    try:
        # Verify admin permission
        if not current_user.get("is_admin"):
            raise ValueError("Admin permission required")
        
        await ws_handler.broadcast_event(
            event_type=event_type,
            data=data,
            user_id=user_id
        )
        
        return {
            "message": "Event broadcast successfully",
            "event_type": event_type,
            "user_id": user_id
        }
    
    except Exception as e:
        logger.log_error(
            "Error broadcasting event",
            error=str(e),
            event_type=event_type,
            data=data,
            user_id=user_id,
            exc_info=True
        )
        raise
