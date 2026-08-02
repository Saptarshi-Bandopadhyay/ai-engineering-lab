from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    Dependency to yield a database session per request.
    Automatically closes the session after the request is complete.
    """
    async with AsyncSessionLocal() as session:
        yield session
