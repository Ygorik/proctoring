from sqlalchemy import select, insert

from src.services.registration.schemas import RegisterData
from src.db.base_db_service import BaseDBService
from src.db.models import UserDB


class RegisterDBService(BaseDBService):
    async def check_login(self, *, login: str) -> bool:
        async with self.get_async_session() as sess, sess.begin():  # noqa
            return bool(
                await sess.scalar(select(UserDB.login).where(UserDB.login == login))
            )

    async def register_user(self, *, register_data: RegisterData) -> UserDB:
        async with self.get_async_session() as sess, sess.begin():  # noqa
            user_db = await sess.scalar(
                insert(UserDB)
                .values(
                    login=register_data.login,
                    hashed_password=register_data.hashed_password,
                )
                .returning(UserDB)
            )

        return user_db
