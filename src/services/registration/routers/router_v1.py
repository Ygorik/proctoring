from fastapi import APIRouter, Depends
from starlette import status

from src.services.authorization.schemas import Token
from src.services.registration.dependencies import register_service_dependency
from src.services.registration.schemas import RegisterData
from src.services.registration.service import RegisterService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_new_user(
    register_data: RegisterData,
    register_service: RegisterService = Depends(register_service_dependency),
) -> Token:
    return await register_service.register_user(register_data=register_data)
