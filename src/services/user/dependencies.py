from fastapi import Depends

from src.services.role.db_service import RoleDBService
from src.services.role.dependencies import role_db_service_dependency
from src.services.user.db_service import UserDBService
from src.services.user.service import UserService
from src.db.base_db_service import Session


async def user_db_service_dependency() -> UserDBService:
    return UserDBService(Session)


async def user_service_dependency(
    user_db_service: UserDBService = Depends(user_db_service_dependency),
    role_db_service: RoleDBService = Depends(role_db_service_dependency),
) -> UserService:
    return UserService(user_db_service=user_db_service, role_db_service=role_db_service)
