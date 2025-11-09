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

STUDENT_ROLE_NAME = "STUDENT"


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

    async def get_user_by_id(self, *, user_id) -> UserDB:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(UserDB)
                .options(
                    selectinload(UserDB.role).load_only(
                        RoleDB.id,
                        RoleDB.name,
                        RoleDB.rights_create,
                        RoleDB.rights_read,
                        RoleDB.rights_update,
                        RoleDB.rights_delete,
                    ),
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

    async def create_student_user(self, *, user_data: SampleUser) -> str:
        async with self.get_async_session() as sess:
            student_role_id = await sess.scalar(select(RoleDB.id).where(RoleDB.name == STUDENT_ROLE_NAME))
            await sess.execute(
                insert(UserDB).values(**user_data.model_dump(exclude_none=True), role_id=student_role_id)
            )
            await sess.commit()
        return user_data.id
