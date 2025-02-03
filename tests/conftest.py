from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import BaseDB, UserDB, ProfileDB
from src.db.base_db_service import Session
from src.main import app

# Use it if you ran tests on windows
# @pytest.fixture(scope="session")
# def event_loop(request: Request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


async def deprecate_db():
    async with Session() as async_sess, async_sess.begin():
        for table in reversed(BaseDB.metadata.sorted_tables):
            await async_sess.execute(table.delete())


@asynccontextmanager
async def override_get_async_session() -> AsyncSession:
    # await deprecate_db()
    async with Session() as async_sess:
        try:
            yield async_sess
        except Exception:
            await async_sess.rollback()
            await async_sess.close()
            raise


app.dependency_overrides["get_async_session"] = override_get_async_session


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://back_app_test") as async_client:
        yield async_client


async def create_user():
    async with override_get_async_session() as sess, sess.begin():
        user_id = await sess.scalar(
            insert(UserDB)
            .values(
                email="used_email@mail.com",
                phone_number="78005553535",
                hashed_password="gAAAAABm2HMzAygNYS4qWUgBklY7MrvjMnH0Svo__0DUyKHTCRdQzSElkiYN93eNJdQsVJmTO4-rZFcZz_yC52iABMcDvdpJ3A==",
            )
            .returning(UserDB.id)
        )

        await sess.execute(
            insert(ProfileDB)
            .values(nickname="used_nickname", user_id=user_id)
            .returning(ProfileDB)
        )


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    await deprecate_db()
    await create_user()
