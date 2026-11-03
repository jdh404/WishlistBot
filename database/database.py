from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .models import Base


def make_session_factory(database_url: str):
    engine = create_async_engine(database_url, echo=False)
    return engine, async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

