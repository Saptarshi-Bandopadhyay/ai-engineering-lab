from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")
user_repo = UserRepository()


async def get_current_user(
    session: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Now completely agnostic to the jwt library
        payload = security.decode_token(token)
        token_data = TokenPayload(**payload)

        if token_data.sub is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = await user_repo.get_user_by_id(session, user_id=int(token_data.sub))

    if not user or not user.is_active:
        raise credentials_exception

    return user
