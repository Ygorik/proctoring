from fastapi import Depends

from src.db.base_db_service import Session
from src.services.role.db_service import RoleDBService
from src.services.role.service import RoleService


async def role_db_service_dependency() -> RoleDBService:
    return RoleDBService(Session)


async def role_service_dependency(
    role_db_service: RoleDBService = Depends(role_db_service_dependency),
) -> RoleService:
    return RoleService(role_db_service=role_db_service)
