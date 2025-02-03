from fastapi import Depends

from src.services.token.dependencies import token_service_dependency
from src.services.token.service import TokenService
from src.services.registration.db_service import RegisterDBService
from src.services.registration.service import RegisterService
from src.db.base_db_service import Session


async def register_db_service_dependency() -> RegisterDBService:
    return RegisterDBService(Session)


async def register_service_dependency(
    register_db_service: RegisterDBService = Depends(register_db_service_dependency),
    token_service: TokenService = Depends(token_service_dependency),
) -> RegisterService:
    return RegisterService(
        register_db_service=register_db_service, token_service=token_service
    )
