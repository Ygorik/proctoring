from src.services.role.db_service import RoleDBService
from src.services.role.exceptions import RoleNotFoundError
from src.services.role.schemas import CreateRoleSchema, RoleItemSchema, PatchRoleSchema


class RoleService:
    def __init__(self, *, role_db_service: RoleDBService) -> None:
        self.role_db_service = role_db_service

    async def create_role(self, *, role_data: CreateRoleSchema) -> None:
        await self.role_db_service.insert_role(role_data)

    async def get_list_of_roles(self) -> list[RoleItemSchema]:
        return [
            RoleItemSchema.from_orm(role)
            for role in await self.role_db_service.get_list_of_roles()
        ]

    async def update_role(self, *, role_id: int, role_data: PatchRoleSchema) -> None:
        await self.get_role_by_id(role_id=role_id)
        await self.role_db_service.update_role(role_id=role_id, role_data=role_data)

    async def delete_role_by_id(self, *, role_id: int) -> None:
        await self.get_role_by_id(role_id=role_id)
        await self.role_db_service.delete_role_by_id(role_id=role_id)

    async def get_role_by_id(self, *, role_id: int) -> RoleItemSchema:
        if role := await self.role_db_service.get_role_by_id(role_id=role_id):
            return RoleItemSchema.from_orm(role)
        raise RoleNotFoundError
