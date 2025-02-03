from fastapi import Depends

from src.db.base_db_service import Session
from src.services.authorization.db_service import AuthorizeDBService
from src.services.authorization.service import AuthorizeService
from src.services.token.dependencies import token_service_dependency
from src.services.token.service import TokenService


async def authorize_db_service_dependency() -> AuthorizeDBService:
    return AuthorizeDBService(Session)


async def authorize_service_dependency(
    authorize_db_service: AuthorizeDBService = Depends(authorize_db_service_dependency),
    token_service: TokenService = Depends(token_service_dependency),
) -> AuthorizeService:
    return AuthorizeService(
        authorize_db_service=authorize_db_service, token_service=token_service
    )
