from fastapi import APIRouter, Depends
from starlette import status


from src.services.authorization.dependencies import authorize_service_dependency
from src.services.authorization.schemas import AuthorizationSchema, Token
from src.services.authorization.service import AuthorizeService


router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK)
async def authorize_user(
    authorization_data: AuthorizationSchema,
    authorize_service: AuthorizeService = Depends(authorize_service_dependency),
) -> Token:
    return await authorize_service.authorize_user(authorization_data=authorization_data)
