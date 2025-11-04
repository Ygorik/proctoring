from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config import settings

engine = create_async_engine(url=settings.db_url, poolclass=NullPool)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class BaseDBService:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session() as async_sess:
            try:
                yield async_sess
            except Exception:
                await async_sess.rollback()
                raise
