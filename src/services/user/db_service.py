from sqlalchemy import select, insert, update, delete, Select
from sqlalchemy.orm import load_only, selectinload

from src.services.proctoring.schemas import SampleUser
from src.services.user.schemas import (
    RegisterData,
    UserItem,
    PatchUserData,
    UserFilters,
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

    async def get_list_of_users(self, *, filters: UserFilters) -> list[UserDB]:
        stmt = (
            select(UserDB)
            .options(
                selectinload(UserDB.role).load_only(RoleDB.name),
                load_only(UserDB.id, UserDB.full_name, UserDB.login),
            )
        )

        stmt = self.filter_user_list(stmt=stmt, filters=filters)

        async with self.get_async_session() as sess:
            return await sess.scalars(stmt)

    @staticmethod
    def filter_user_list(*, stmt: Select, filters: UserFilters) -> Select:
        if filters.subject_id:
            stmt = stmt.join(SubjectUserDB).where(
                SubjectUserDB.subject_id == filters.subject_id
            )
        if filters.role_id:
            stmt = stmt.where(UserDB.role_id == filters.role_id)

        return stmt

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

    async def patch_user_by_id(self, *, user_id: int, user_data: PatchUserData) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(UserDB)
                .values(
                    **user_data.model_dump(exclude={"password"}, exclude_unset=True)
                )
                .where(UserDB.id == user_id)
            )
            await sess.commit()

    async def delete_user_by_id(self, *, user_id: int) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(delete(UserDB).where(UserDB.id == user_id))
            await sess.commit()

    async def create_student_user(self, *, user_data: SampleUser) -> int:
        async with self.get_async_session() as sess:
            user_id = await sess.scalar(insert(UserDB).values(**user_data.model_dump(exclude_none=True)))
            await sess.commit()
        return user_id

    async def get_user_by_name(self, *, name: str) -> UserDB:
        async with self.get_async_session() as sess:
            return await sess.scalar(select(UserDB).where(UserDB.full_name == name))
