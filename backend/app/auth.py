import os
import secrets
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Generate a default API key if not set in environment
DEFAULT_API_KEY = "vpt_" + secrets.token_urlsafe(32)

class APIKeyAuth:
    def __init__(self):
        # Try to get API key from environment, fallback to default
        self.api_key = os.getenv("VPT_API_KEY", DEFAULT_API_KEY)

        # Print the API key on startup for easy setup
        if os.getenv("VPT_API_KEY") is None:
            print(f"⚠️  No VPT_API_KEY environment variable set!")
            print(f"🔑 Using default API key: {self.api_key}")
            print(f"💡 Set VPT_API_KEY environment variable to use a custom key")
        else:
            print(f"🔑 Using API key from environment variable")

    def verify_api_key(self, api_key: str) -> bool:
        """Verify if the provided API key is valid"""
        return api_key == self.api_key

    def get_api_key(self) -> str:
        """Get the current API key"""
        return self.api_key

# Create global instance
api_key_auth = APIKeyAuth()

# Security scheme for FastAPI docs
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to verify API key from Authorization header
    Expected format: Authorization: Bearer <api_key>
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not api_key_auth.verify_api_key(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials

async def verify_api_key_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """
    Optional API key verification for endpoints that might not require auth
    """
    if not credentials:
        return None

    if not api_key_auth.verify_api_key(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials

def verify_websocket_api_key(api_key: str) -> bool:
    """
    Verify API key for WebSocket connections
    """
    return api_key_auth.verify_api_key(api_key)
