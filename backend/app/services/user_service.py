from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import DuplicateResourceError
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user import UserCreate


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    async def register_user(self, session: AsyncSession, user_in: UserCreate) -> User:
        """Handles the core business logic for user registration."""

        # 1. Check for duplicates
        existing_user = await self.user_repo.get_user_by_email(session, user_in.email)
        if existing_user:
            raise DuplicateResourceError("A user with this email already exists.")

        # 2. Hash the password
        hashed_password = get_password_hash(user_in.password)

        # 3. Save to database
        new_user = await self.user_repo.create_user(
            session=session, email=user_in.email, hashed_password=hashed_password
        )

        return new_user
