from typing import Sequence

from sqlalchemy import insert, select, update, delete

from src.db.base_db_service import BaseDBService
from src.db.models import RoleDB, UserDB
from src.services.role.schemas import CreateRoleSchema, PatchRoleSchema


class RoleDBService(BaseDBService):
    async def insert_role(self, role_data: CreateRoleSchema) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(insert(RoleDB).values(**role_data.dict()))
            await sess.commit()

    async def get_list_of_roles(self) -> Sequence[RoleDB]:
        async with self.get_async_session() as sess:
            return await sess.scalars(select(RoleDB))

    async def update_role(self, *, role_id: int, role_data: PatchRoleSchema) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(RoleDB)
                .values(**role_data.model_dump(exclude_unset=True))
                .where(RoleDB.id == role_id)
            )
            await sess.commit()

    async def check_user_have_role(self, *, role_id: int) -> bool:
        async with self.get_async_session() as sess:
            return bool(
                await sess.scalar(
                    select(UserDB.id).join(RoleDB).where(RoleDB.id == role_id)
                )
            )

    async def delete_role_by_id(self, *, role_id: int) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(delete(RoleDB).where(RoleDB.id == role_id))
            await sess.commit()

    async def get_role_by_id(self, *, role_id: int) -> RoleDB:
        async with self.get_async_session() as sess:
            return await sess.scalar(select(RoleDB).where(RoleDB.id == role_id))
