"""Authentication and user management endpoints.

Implements:
- POST /api/v1/auth/register (Citizen user registration with Bcrypt password hashing)
- POST /api/v1/auth/login (Login with JSON or form-urlencoded returning JWT)
- GET /api/v1/auth/me (Current authenticated user profile)
"""

import json
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

try:
    from app.api.deps import get_current_user, get_db
    from app.core.security import (
        create_access_token,
        hash_password,
        verify_password,
    )
    from app.models.user import User
    from app.schemas.auth import (
        LoginRequest,
        LoginResponse,
        RegisterRequest,
        RegisterResponse,
        TokenResponseData,
        UserResponse,
        UserSummary,
    )
except ImportError:
    from backend.app.api.deps import get_current_user, get_db
    from backend.app.core.security import (
        create_access_token,
        hash_password,
        verify_password,
    )
    from backend.app.models.user import User
    from backend.app.schemas.auth import (
        LoginRequest,
        LoginResponse,
        RegisterRequest,
        RegisterResponse,
        TokenResponseData,
        UserResponse,
        UserSummary,
    )

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new citizen user",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    """Register a new citizen user account.
    
    Verifies email uniqueness, hashes password with native bcrypt,
    and returns 201 Created with the public UserSummary.
    """
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role="user",
        phone_number=payload.phone_number,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RegisterResponse(
        status="success",
        message="User registered successfully",
        data=UserSummary.model_validate(new_user),
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT token",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "format": "email", "example": "admin@bilcode.id"},
                            "password": {"type": "string", "example": "Admin123!"},
                        },
                        "required": ["email", "password"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "example": "admin@bilcode.id"},
                            "password": {"type": "string", "example": "Admin123!"},
                        },
                        "required": ["username", "password"],
                    }
                },
            }
        }
    },
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Authenticate user credentials and return a signed HS256 JWT access token.
    
    Supports both JSON and application/x-www-form-urlencoded payloads.
    """
    content_type = request.headers.get("content-type", "")
    email: Any = None
    password: Any = None

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid JSON payload",
            )
        if not isinstance(body, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="JSON body must be an object",
            )
        email = body.get("email") or body.get("username")
        password = body.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email and password are required",
        )

    user = db.query(User).filter(User.email == str(email)).first()
    if user is None or not verify_password(str(password), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

    return LoginResponse(
        status="success",
        data=TokenResponseData(
            access_token=access_token,
            token_type="bearer",
            user=UserSummary.model_validate(user),
        ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retrieve the authenticated user's profile and assigned role."""
    return UserResponse(
        status="success",
        data=UserSummary.model_validate(current_user),
    )
