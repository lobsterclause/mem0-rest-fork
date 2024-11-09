"""Error handlers for memory system."""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import pytz
from fastapi import Request, WebSocket, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handler for application errors."""

    async def handle_http_error(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle HTTP errors."""
        try:
            # Get error details
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_type = "InternalServerError"
            error_message = str(exc)
            
            if isinstance(exc, HTTPException):
                status_code = exc.status_code
                error_type = exc.__class__.__name__
                error_message = exc.detail
            
            # Log error
            logger.error(
                "HTTP error occurred: type=%s, message=%s, status=%d, path=%s, method=%s",
                error_type,
                error_message,
                status_code,
                str(request.url),
                request.method,
                exc_info=True
            )
            
            # Create error response
            error_response = {
                "error": {
                    "type": error_type,
                    "message": error_message,
                    "status": status_code,
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat(),
                    "path": str(request.url),
                    "method": request.method
                }
            }
            
            return JSONResponse(
                status_code=status_code,
                content=error_response
            )
        
        except Exception as e:
            logger.error(
                "Failed to handle HTTP error: %s, original_error=%s",
                str(e),
                str(exc),
                exc_info=True
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "message": "An unexpected error occurred",
                        "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                    }
                }
            )

    async def handle_websocket_error(
        self,
        websocket: WebSocket,
        exc: Exception
    ) -> Optional[Dict[str, Any]]:
        """Handle WebSocket errors."""
        try:
            # Get error details
            error_type = exc.__class__.__name__
            error_message = str(exc)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            if isinstance(exc, HTTPException):
                status_code = exc.status_code
                error_message = exc.detail
            
            # Log error
            logger.error(
                "WebSocket error occurred: type=%s, message=%s, status=%d, client=%s",
                error_type,
                error_message,
                status_code,
                str(websocket.client),
                exc_info=True
            )
            
            # Create error message
            error_message = {
                "type": "error",
                "data": {
                    "type": error_type,
                    "message": error_message,
                    "status": status_code,
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            }
            
            # Try to send error message
            try:
                if websocket.client_state.CONNECTED:
                    await websocket.send_json(error_message)
            except Exception:
                pass
            
            return error_message
        
        except Exception as e:
            logger.error(
                "Failed to handle WebSocket error: %s, original_error=%s",
                str(e),
                str(exc),
                exc_info=True
            )
            return {
                "type": "error",
                "data": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.now(pytz.timezone("US/Pacific")).isoformat()
                }
            }

    async def handle_startup_error(
        self,
        exc: Exception
    ):
        """Handle application startup errors."""
        try:
            logger.error(
                "Application startup error: %s",
                str(exc),
                exc_info=True
            )
            # Exit application on startup error
            exit(1)
        
        except Exception as e:
            logger.error(
                "Failed to handle startup error: %s, original_error=%s",
                str(e),
                str(exc),
                exc_info=True
            )
            exit(1)

    async def handle_shutdown_error(
        self,
        exc: Exception
    ):
        """Handle application shutdown errors."""
        try:
            logger.error(
                "Application shutdown error: %s",
                str(exc),
                exc_info=True
            )
        
        except Exception as e:
            logger.error(
                "Failed to handle shutdown error: %s, original_error=%s",
                str(e),
                str(exc),
                exc_info=True
            )

# Global error handler instance
error_handler = ErrorHandler()

# Exception handlers
http_exception_handler = error_handler.handle_http_error
websocket_exception_handler = error_handler.handle_websocket_error
startup_exception_handler = error_handler.handle_startup_error
shutdown_exception_handler = error_handler.handle_shutdown_error
