from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker | None = None


def init_engine() -> AsyncEngine:
    global engine, AsyncSessionLocal
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
    )
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine


async def close_engine():
    global engine
    if engine:
        await engine.dispose()
        engine = None


async def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("Database engine not initialized.")
    async with AsyncSessionLocal() as session:
        yield session
