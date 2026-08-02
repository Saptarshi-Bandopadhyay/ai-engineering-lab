from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core import security
from backend.app.core.exceptions import InvalidCredentialsError
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.token import Token


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    async def authenticate_user(
        self, session: AsyncSession, email: str, password: str
    ) -> Token:
        user = await self.user_repo.get_user_by_email(session, email)

        if not user or not security.verify_password(password, user.hashed_password):
            # Raising our custom pure-Python exception
            raise InvalidCredentialsError("Incorrect email or password")

        access_token = security.create_access_token(subject=user.id)

        return Token(access_token=access_token, token_type="bearer", user=user)
