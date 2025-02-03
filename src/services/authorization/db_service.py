from uuid import UUID

from sqlalchemy import select, insert

from src.db.base_db_service import BaseDBService
from src.db.models import UserDB
from src.db.models.authorization_model import AuthorizationDB


class AuthorizeDBService(BaseDBService):
    async def get_user_by_login(self, *, login: str) -> UserDB:
        async with self.get_async_session() as sess, sess.begin():
            return await sess.scalar(select(UserDB).where(UserDB.login == login))

    async def insert_authorization(self, *, user_id: UUID) -> None:
        async with self.get_async_session() as sess, sess.begin():
            return await sess.scalar(insert(AuthorizationDB).values(user_id=user_id))
