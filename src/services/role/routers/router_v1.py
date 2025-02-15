from fastapi import APIRouter, Depends, Query
from starlette import status

from src.services.authorization.schemas import User
from src.services.role.dependencies import role_service_dependency
from src.services.role.schemas import CreateRoleSchema, RoleItemSchema, PatchRoleSchema
from src.services.role.service import RoleService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: CreateRoleSchema,
    role_service: RoleService = Depends(role_service_dependency),
) -> None:
    await role_service.create_role(role_data=role_data)


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_roles(
    role_service: RoleService = Depends(role_service_dependency),
    user: User = Depends(decode_user_token)
) -> list[RoleItemSchema]:
    return await role_service.get_list_of_roles(user=user)


@router.patch("/{roleId}", status_code=status.HTTP_200_OK)
async def patch_role(
    role_data: PatchRoleSchema,
    role_id: int = Query(alias="roleId"),
    role_service: RoleService = Depends(role_service_dependency),
) -> None:
    await role_service.update_role(role_id=role_id, role_data=role_data)


@router.delete("/{roleId}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: int = Query(alias="roleId"),
    role_service: RoleService = Depends(role_service_dependency),
) -> None:
    return await role_service.delete_role_by_id(role_id=role_id)


@router.get("/{roleId}", status_code=status.HTTP_200_OK)
async def get_role(
    role_id: int = Query(alias="roleId"),
    role_service: RoleService = Depends(role_service_dependency),
) -> RoleItemSchema:
    return await role_service.get_role_by_id(role_id=role_id)
