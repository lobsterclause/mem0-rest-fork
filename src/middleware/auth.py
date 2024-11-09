"""Authentication middleware for memory system."""
from typing import Optional
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.config import settings
from src.utils.logging import LoggerMixin

security = HTTPBearer()
logger = LoggerMixin()

class AuthHandler:
    """Handler for authentication."""

    def __init__(self):
        """Initialize authentication handler."""
        self.secret = settings.jwt_secret
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=settings.refresh_token_expire_days)

    def create_access_token(
        self,
        user_id: str,
        additional_claims: Optional[dict] = None
    ) -> str:
        """Create access token."""
        try:
            claims = {
                "user_id": user_id,
                "exp": datetime.utcnow() + self.access_token_expire,
                "type": "access"
            }
            if additional_claims:
                claims.update(additional_claims)
            
            return jwt.encode(
                claims,
                self.secret,
                algorithm=self.algorithm
            )
        
        except Exception as e:
            logger.log_error(
                "Failed to create access token",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            raise

    def create_refresh_token(
        self,
        user_id: str,
        additional_claims: Optional[dict] = None
    ) -> str:
        """Create refresh token."""
        try:
            claims = {
                "user_id": user_id,
                "exp": datetime.utcnow() + self.refresh_token_expire,
                "type": "refresh"
            }
            if additional_claims:
                claims.update(additional_claims)
            
            return jwt.encode(
                claims,
                self.secret,
                algorithm=self.algorithm
            )
        
        except Exception as e:
            logger.log_error(
                "Failed to create refresh token",
                error=str(e),
                user_id=user_id,
                exc_info=True
            )
            raise

    def decode_token(self, token: str) -> dict:
        """Decode and validate token."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            
            if payload.get("type") not in ["access", "refresh"]:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            logger.log_error(
                "Failed to decode token",
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=401,
                detail="Failed to decode token"
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> dict:
        """Get current user from token."""
        try:
            payload = self.decode_token(credentials.credentials)
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )
            
            return {
                "id": payload.get("user_id"),
                "is_admin": payload.get("is_admin", False)
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.log_error(
                "Failed to get current user",
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=401,
                detail="Failed to authenticate"
            )

    async def get_websocket_user(self, websocket: WebSocket) -> dict:
        """Get user from WebSocket connection."""
        try:
            # Get token from query parameters
            token = websocket.query_params.get("token")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Token not found"
                )
            
            payload = self.decode_token(token)
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )
            
            return {
                "id": payload.get("user_id"),
                "is_admin": payload.get("is_admin", False)
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.log_error(
                "Failed to get WebSocket user",
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=401,
                detail="Failed to authenticate WebSocket"
            )

    async def refresh_tokens(self, refresh_token: str) -> dict:
        """Refresh access and refresh tokens."""
        try:
            payload = self.decode_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("user_id")
            additional_claims = {
                k: v for k, v in payload.items()
                if k not in ["user_id", "exp", "type"]
            }
            
            access_token = self.create_access_token(
                user_id=user_id,
                additional_claims=additional_claims
            )
            new_refresh_token = self.create_refresh_token(
                user_id=user_id,
                additional_claims=additional_claims
            )
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.log_error(
                "Failed to refresh tokens",
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=401,
                detail="Failed to refresh tokens"
            )

# Global auth handler instance
auth_handler = AuthHandler()

# Dependency for getting current user
get_current_user = auth_handler.get_current_user

# Dependency for getting WebSocket user
get_websocket_user = auth_handler.get_websocket_user
