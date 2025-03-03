from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import load_only, selectinload

from src.services.user.schemas import (
    RegisterData,
    UserItemForList,
    UserItem,
    PatchUserData,
)
from src.db.base_db_service import BaseDBService
from src.db.models import UserDB, RoleDB, SubjectUserDB


class UserDBService(BaseDBService):
    async def check_login(self, *, login: str) -> bool:
        async with self.get_async_session() as sess:
            return bool(
                await sess.scalar(select(UserDB.login).where(UserDB.login == login))
            )

    async def register_user(self, *, register_data: RegisterData) -> None:
        async with self.get_async_session() as sess, sess.begin():
            await sess.scalar(
                insert(UserDB).values(**register_data.model_dump(exclude={"password"}))
            )

    async def get_list_of_users(self) -> list[UserItemForList]:
        async with self.get_async_session() as sess:
            return await sess.scalars(
                select(UserDB).options(
                    load_only(UserDB.id, UserDB.full_name, UserDB.login)
                )
            )

    async def get_user_by_id(self, *, user_id) -> UserItem:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(UserDB, RoleDB)
                .options(
                    selectinload(UserDB.role),
                    load_only(
                        UserDB.id,
                        UserDB.full_name,
                        UserDB.login,
                        UserDB.hashed_password,
                    ),
                )
                .where(UserDB.id == user_id)
            )

    async def patch_user_by_id(self, *, user_id: str, user_data: PatchUserData) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(UserDB)
                .values(
                    **user_data.model_dump(exclude={"password"}, exclude_unset=True)
                )
                .where(UserDB.id == user_id)
            )
            await sess.commit()

    async def delete_user_by_id(self, *, user_id: str) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(delete(UserDB).where(UserDB.id == user_id))
            await sess.commit()

    async def get_users_by_subject_id(self, *, subject_id: int) -> list[UserItem]:
        async with self.get_async_session() as sess:
            return await sess.scalars(
                select(UserDB)
                .join(SubjectUserDB)
                .where(SubjectUserDB.subject_id == subject_id)
                .where(SubjectUserDB.user_id == UserDB.id)
            )
