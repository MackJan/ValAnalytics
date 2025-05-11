import os
from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Pull in the URL from env; in Docker Compose this will be set to point at the "postgres" service
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/valorant"
)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def init_db() -> None:
    """
    Initialize the database (create tables).
    Call this on application startup before serving requests.
    """
    async with engine.begin() as conn:
        # Create all tables based on SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)