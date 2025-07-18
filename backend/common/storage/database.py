from uuid import uuid4
from contextlib import asynccontextmanager
from asyncpg import Connection
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from typing_extensions import AsyncGenerator

from common.core.config import settings


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid4()}__'


def create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.db_url,
        poolclass=NullPool,
        connect_args={
            'connection_class': CConnection,
        },
    )


def create_session(_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


engine = create_engine()
async_session = create_session(engine)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()  # Явное закрытие сессии
