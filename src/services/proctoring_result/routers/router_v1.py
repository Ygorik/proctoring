from fastapi import APIRouter, Depends, Path
from starlette import status

from src.services.authorization.schemas import User
from src.services.proctoring_result.dependencies import (
    proctoring_result_service_dependency,
)
from src.services.proctoring_result.schemas import (
    ProctoringResultFilters,
    ProctoringResultItemSchema,
    PatchProctoringResultSchema,
)
from src.services.proctoring_result.service import ProctoringResultService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def get_proctoring_result_list(
    proctoring_result_service: ProctoringResultService = Depends(
        proctoring_result_service_dependency
    ),
    filters: ProctoringResultFilters = Depends(),
    user: User = Depends(decode_user_token),
) -> list[ProctoringResultItemSchema]:
    return await proctoring_result_service.get_proctoring_result_list(
        user=user, filters=filters
    )


@router.get("/{proctoringResultId}", status_code=status.HTTP_200_OK)
async def get_proctoring_result(
    proctoring_result_id: int = Path(alias="proctoringResultId"),
    proctoring_result_service: ProctoringResultService = Depends(
        proctoring_result_service_dependency
    ),
    user: User = Depends(decode_user_token),
) -> ProctoringResultItemSchema:
    return await proctoring_result_service.get_proctoring_result_by_id(
        user=user, proctoring_result_id=proctoring_result_id
    )


@router.patch("/{proctoringResultId}", status_code=status.HTTP_200_OK)
async def patch_proctoring_result(
    proctoring_result_data: PatchProctoringResultSchema,
    proctoring_result_id: int = Path(alias="proctoringResultId"),
    proctoring_result_service: ProctoringResultService = Depends(
        proctoring_result_service_dependency
    ),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_result_service.update_proctoring_result(
        user=user,
        proctoring_result_id=proctoring_result_id,
        proctoring_result_data=proctoring_result_data,
    )


@router.delete("/{proctoringResultId}", status_code=status.HTTP_200_OK)
async def delete_proctoring_result(
    proctoring_result_id: int = Path(alias="proctoringResultId"),
    proctoring_result_service: ProctoringResultService = Depends(
        proctoring_result_service_dependency
    ),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_result_service.delete_proctoring_result(
        user=user,
        proctoring_result_id=proctoring_result_id,
    )
