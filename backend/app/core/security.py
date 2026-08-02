from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from backend.app.core.config import settings

# Initializes pwdlib with the recommended Argon2 configuration
password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(subject: str | int) -> str:
    """Generates a JWT access token expiring in 15 minutes."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {"sub": str(subject), "exp": expire, "iat": datetime.now(UTC)}

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodes a JWT. Raises jwt.exceptions.InvalidTokenError if invalid."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
