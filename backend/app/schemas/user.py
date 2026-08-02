from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    # EmailStr automatically validates standard email formatting
    email: EmailStr
    # Enforces the minimum 8-character rule from the ticket
    password: str = Field(
        min_length=8, description="Password must be at least 8 characters long"
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    # Allows Pydantic to read directly from the SQLAlchemy model object
    model_config = ConfigDict(from_attributes=True)
