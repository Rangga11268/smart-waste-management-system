"""FastAPI common dependencies for database sessions and authentication."""

from typing import Generator, Optional
import uuid
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

try:
    from app.core.config import settings
    from app.core.database import get_db
    from app.core.security import JWTError, decode_access_token
    from app.models.user import User
except ImportError:
    from backend.app.core.config import settings
    from backend.app.core.database import get_db
    from backend.app.core.security import JWTError, decode_access_token
    from backend.app.models.user import User

# Re-export get_db
__all__ = ["get_db", "oauth2_scheme", "get_current_user", "get_current_admin"]

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer JWT token and return active authenticated User model.
    
    Raises 401 Unauthorized if missing, expired, malformed, or inactive.
    """
    if not token:
        # Fallback inspection of Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
        sub: Optional[str] = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_uuid = uuid.UUID(str(sub))
    except (JWTError, jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Guard dependency ensuring the authenticated user has 'admin' role.
    
    Raises 403 Forbidden if current_user.role is not 'admin'.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
