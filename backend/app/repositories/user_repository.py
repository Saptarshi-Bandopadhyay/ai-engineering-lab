from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User


class UserRepository:
    async def get_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        """Fetch a user by email to check for duplicates."""
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self, session: AsyncSession, email: str, hashed_password: str
    ) -> User:
        """Insert a new user into the database."""
        new_user = User(
            email=email,
            # For this MVP, we'll derive a simple username from the email
            username=email.split("@")[0],
            hashed_password=hashed_password,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        """Fetch a user by their primary key."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
