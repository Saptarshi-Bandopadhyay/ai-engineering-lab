import asyncio

from sqlalchemy import text

from backend.app.db.session import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as session:
        print(
            "database =",
            await session.scalar(text("select current_database()")),
        )
        print(
            "user =",
            await session.scalar(text("select current_user")),
        )
        print(
            "search_path =",
            await session.scalar(text("show search_path")),
        )


asyncio.run(main())
