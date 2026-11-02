"""Security utilities for password hashing and JWT token handling.

Native bcrypt password hashing (Python 3.12 compatible) and PyJWT
HS256 access token creation and decoding.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt

try:
    from app.core.config import settings
except ImportError:
    from backend.app.core.config import settings


# Expose JWTError for callers
JWTError = jwt.PyJWTError


def hash_password(password: str) -> str:
    """Hash password using native bcrypt (Python 3.12 compatible)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Encode HS256 JWT using settings.JWT_SECRET with exp timestamp.
    
    Payload data must include 'sub' (str user UUID), 'email', and 'role'.
    """
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode HS256 JWT using settings.JWT_SECRET and settings.ALGORITHM.
    
    Raises JWTError on expired or invalid signature.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError as exc:
        raise JWTError(str(exc)) from exc
