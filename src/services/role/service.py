from src.services.authorization.schemas import User
from src.services.role.db_service import RoleDBService
from src.services.role.exceptions import RoleNotFoundError
from src.services.role.schemas import CreateRoleSchema, RoleItemSchema, PatchRoleSchema
from src.utils.role_checker import check_read_rights, check_delete_rights, check_update_rights, check_create_rights


class RoleService:
    def __init__(self, *, role_db_service: RoleDBService) -> None:
        self.role_db_service = role_db_service

    @check_create_rights
    async def create_role(self, *, role_data: CreateRoleSchema) -> None:
        await self.role_db_service.insert_role(role_data)

    @check_read_rights
    async def get_list_of_roles(self) -> list[RoleItemSchema]:
        return [
            RoleItemSchema.from_orm(role)
            for role in await self.role_db_service.get_list_of_roles()
        ]

    @check_read_rights
    async def get_role_by_id(self, *, role_id: int) -> RoleItemSchema:
        return await self.get_role_by_id_if_exist(role_id=role_id)

    @check_update_rights
    async def update_role(self, *, role_id: int, role_data: PatchRoleSchema) -> None:
        await self.get_role_by_id_if_exist(role_id=role_id)
        await self.role_db_service.update_role(role_id=role_id, role_data=role_data)

    @check_delete_rights
    async def delete_role_by_id(self, *, role_id: int) -> None:
        await self.get_role_by_id_if_exist(role_id=role_id)
        await self.role_db_service.delete_role_by_id(role_id=role_id)

    async def get_role_by_id_if_exist(self, *, role_id) -> RoleItemSchema:
        if role := await self.role_db_service.get_role_by_id(role_id=role_id):
            return RoleItemSchema.from_orm(role)
        raise RoleNotFoundError