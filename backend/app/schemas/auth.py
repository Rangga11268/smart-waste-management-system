"""Pydantic schemas for authentication and user endpoints."""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Payload schema for user registration."""

    full_name: str = Field(..., min_length=1, max_length=150, description="Full legal name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=6, description="Plaintext user password")
    phone_number: Optional[str] = Field(None, max_length=30, description="Contact phone number")


class LoginRequest(BaseModel):
    """Payload schema for user login via JSON."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserSummary(BaseModel):
    """Public user profile summary schema."""

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponseData(BaseModel):
    """Token payload data returned on successful login."""

    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class RegisterResponse(BaseModel):
    """Enveloped response for POST /api/v1/auth/register."""

    status: str = "success"
    message: str = "User registered successfully"
    data: UserSummary


class LoginResponse(BaseModel):
    """Enveloped response for POST /api/v1/auth/login."""

    status: str = "success"
    data: TokenResponseData


class UserResponse(BaseModel):
    """Enveloped response for GET /api/v1/auth/me."""

    status: str = "success"
    data: UserSummary
