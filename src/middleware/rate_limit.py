"""Rate limiting middleware for memory system."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from fastapi import HTTPException, Request, WebSocket
from ..utils.logging import LoggerMixin

class RateLimiter(LoggerMixin):
    """Rate limiter for API requests."""

    def __init__(self):
        """Initialize rate limiter."""
        super().__init__()
        self.requests: Dict[str, list] = {}
        self.ws_messages: Dict[str, list] = {}
        
        # Configure limits
        self.http_rate_limit = 100  # requests per minute
        self.ws_rate_limit = 50  # messages per minute
        self.window = 60  # seconds
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_requests())

    async def check_http_rate_limit(
        self,
        request: Request,
        user_id: Optional[str] = None
    ):
        """Check rate limit for HTTP requests."""
        try:
            # Get client identifier
            client_id = user_id or request.client.host
            if not client_id:
                raise HTTPException(
                    status_code=400,
                    detail="Client identifier not found"
                )
            
            # Get current timestamp
            now = datetime.utcnow()
            
            # Initialize request list for client
            if client_id not in self.requests:
                self.requests[client_id] = []
            
            # Remove old requests
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if now - ts < timedelta(seconds=self.window)
            ]
            
            # Check rate limit
            if len(self.requests[client_id]) >= self.http_rate_limit:
                self.log_warning(
                    "HTTP rate limit exceeded",
                    client_id=client_id,
                    request_count=len(self.requests[client_id])
                )
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
            
            # Add current request
            self.requests[client_id].append(now)
        
        except HTTPException:
            raise
        except Exception as e:
            self.log_error(
                "Error checking HTTP rate limit",
                error=str(e),
                client_id=user_id or request.client.host,
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="Error checking rate limit"
            )

    async def check_ws_rate_limit(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None
    ) -> bool:
        """Check rate limit for WebSocket messages."""
        try:
            # Get client identifier
            client_id = user_id or websocket.client.host
            if not client_id:
                return False
            
            # Get current timestamp
            now = datetime.utcnow()
            
            # Initialize message list for client
            if client_id not in self.ws_messages:
                self.ws_messages[client_id] = []
            
            # Remove old messages
            self.ws_messages[client_id] = [
                ts for ts in self.ws_messages[client_id]
                if now - ts < timedelta(seconds=self.window)
            ]
            
            # Check rate limit
            if len(self.ws_messages[client_id]) >= self.ws_rate_limit:
                self.log_warning(
                    "WebSocket rate limit exceeded",
                    client_id=client_id,
                    message_count=len(self.ws_messages[client_id])
                )
                return False
            
            # Add current message
            self.ws_messages[client_id].append(now)
            return True
        
        except Exception as e:
            self.log_error(
                "Error checking WebSocket rate limit",
                error=str(e),
                client_id=user_id or websocket.client.host,
                exc_info=True
            )
            return False

    async def _cleanup_old_requests(self):
        """Clean up old requests periodically."""
        try:
            while True:
                await asyncio.sleep(self.window)
                
                now = datetime.utcnow()
                window_delta = timedelta(seconds=self.window)
                
                # Clean up HTTP requests
                for client_id in list(self.requests.keys()):
                    self.requests[client_id] = [
                        ts for ts in self.requests[client_id]
                        if now - ts < window_delta
                    ]
                    if not self.requests[client_id]:
                        del self.requests[client_id]
                
                # Clean up WebSocket messages
                for client_id in list(self.ws_messages.keys()):
                    self.ws_messages[client_id] = [
                        ts for ts in self.ws_messages[client_id]
                        if now - ts < window_delta
                    ]
                    if not self.ws_messages[client_id]:
                        del self.ws_messages[client_id]
                
                self.log_debug(
                    "Cleaned up old requests",
                    http_clients=len(self.requests),
                    ws_clients=len(self.ws_messages)
                )
        
        except Exception as e:
            self.log_error(
                "Error cleaning up old requests",
                error=str(e),
                exc_info=True
            )

    async def get_rate_limit_headers(
        self,
        client_id: str
    ) -> Dict[str, Any]:
        """Get rate limit headers for response."""
        try:
            # Get current counts
            http_count = len(self.requests.get(client_id, []))
            ws_count = len(self.ws_messages.get(client_id, []))
            
            return {
                "X-RateLimit-Limit": str(self.http_rate_limit),
                "X-RateLimit-Remaining": str(max(0, self.http_rate_limit - http_count)),
                "X-RateLimit-Reset": str(self.window),
                "X-WS-RateLimit-Limit": str(self.ws_rate_limit),
                "X-WS-RateLimit-Remaining": str(max(0, self.ws_rate_limit - ws_count)),
                "X-WS-RateLimit-Reset": str(self.window)
            }
        
        except Exception as e:
            self.log_error(
                "Error getting rate limit headers",
                error=str(e),
                client_id=client_id,
                exc_info=True
            )
            return {}

# Global rate limiter instance
rate_limiter = RateLimiter()

# Dependency for checking HTTP rate limit
check_http_rate_limit = rate_limiter.check_http_rate_limit

# Dependency for checking WebSocket rate limit
check_ws_rate_limit = rate_limiter.check_ws_rate_limit
