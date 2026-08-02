from pydantic import BaseModel

from backend.app.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse  # Enriched response for the frontend


class TokenPayload(BaseModel):
    sub: str | None = None
