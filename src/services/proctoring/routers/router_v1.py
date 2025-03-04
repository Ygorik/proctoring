from fastapi import APIRouter, Depends, Path
from starlette import status

from src.services.authorization.schemas import User
from src.services.proctoring.dependencies import proctoring_service_dependency
from src.services.proctoring.schemas import CreateProctoringSchema, ProctoringItemSchema, PatchProctoringSchema
from src.services.proctoring.service import ProctoringService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_proctoring(
    proctoring_data: CreateProctoringSchema,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.create_proctoring(user=user, proctoring_data=proctoring_data)


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_proctoring(
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[ProctoringItemSchema]:
    return await proctoring_service.get_list_of_proctoring(user=user)


@router.get("/{proctoringId}", status_code=status.HTTP_200_OK)
async def get_proctoring(
    proctoring_id: int = Path(alias="proctoringId"),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> ProctoringItemSchema:
    return await proctoring_service.get_proctoring_by_id(user=user, proctoring_id=proctoring_id)


@router.patch("/{proctoringId}", status_code=status.HTTP_200_OK)
async def patch_proctoring(
    proctoring_data: PatchProctoringSchema,
    proctoring_id: int,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.update_proctoring(user=user, proctoring_id=proctoring_id, proctoring_data=proctoring_data)


@router.delete("/{proctoringId}", status_code=status.HTTP_200_OK)
async def delete_proctoring(
    proctoring_id: int,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    return await proctoring_service.delete_proctoring_by_id(user=user, proctoring_id=proctoring_id)
