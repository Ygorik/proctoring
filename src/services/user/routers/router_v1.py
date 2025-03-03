from fastapi import APIRouter, Depends, Path, Query
from starlette import status

from src.services.authorization.schemas import User
from src.services.user.dependencies import user_service_dependency
from src.services.user.schemas import (
    RegisterData,
    UserItemForList,
    UserItem,
    PatchUserData,
)
from src.services.user.service import UserService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def user_new_user(
    register_data: RegisterData,
    user_service: UserService = Depends(user_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    return await user_service.register_user(user=user, register_data=register_data)


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_users(
    user_service: UserService = Depends(user_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[UserItemForList]:
    return await user_service.get_list_of_users(user=user)


@router.get("/subjectUsers", status_code=status.HTTP_200_OK)
async def get_subject_users(
    subject_id: int = Query(alias="subjectId"),
    user_service: UserService = Depends(user_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[UserItemForList]:
    return await user_service.get_subject_users(user=user, subject_id=subject_id)


@router.get("/{userId}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: str = Path(alias="userId"),
    user_service: UserService = Depends(user_service_dependency),
    user: User = Depends(decode_user_token),
) -> UserItem:
    return await user_service.get_user_by_id(user=user, user_id=user_id)


@router.patch("/{userId}", status_code=status.HTTP_200_OK)
async def patch_user_by_id(
    user_data: PatchUserData,
    user_id: str = Path(alias="userId"),
    user_service: UserService = Depends(user_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await user_service.patch_user_by_id(user=user, user_id=user_id, user_data=user_data)


@router.delete("/{userId}", status_code=status.HTTP_200_OK)
async def delete_user_by_id(
    user_id: str = Path(alias="userId"),
    user_service: UserService = Depends(user_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await user_service.delete_user_by_id(user=user, user_id=user_id)
