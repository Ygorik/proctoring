from fastapi import APIRouter, Depends, Path, UploadFile, Query
from starlette import status

from src.services.authorization.schemas import User
from src.services.proctoring.dependencies import proctoring_service_dependency
from src.services.proctoring.schemas import (
    CreateProctoringSchema,
    ProctoringTypeItemSchema,
    PatchProctoringSchema,
    CreateProctoringTypeSchema,
    ProctoringItemSchema,
    UpdateProctoringTypeSchema,
    ProctoringFilters,
    SampleData,
)
from src.services.proctoring.service import ProctoringService
from src.services.token.service import decode_user_token
from src.utils.moodle_auth import check_moodle_token

router = APIRouter()


@router.post("/proctoringType", status_code=status.HTTP_201_CREATED)
async def create_proctoring_type(
    proctoring_type_data: CreateProctoringTypeSchema,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.create_proctoring_type(
        user=user, proctoring_type_data=proctoring_type_data
    )


@router.get("/proctoringType", status_code=status.HTTP_200_OK)
async def get_list_of_proctoring_types(
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[ProctoringTypeItemSchema]:
    return await proctoring_service.get_list_of_proctoring_types(user=user)


@router.get("/proctoringType/{proctoringTypeId}", status_code=status.HTTP_200_OK)
async def get_proctoring(
    proctoring_type_id: int = Path(alias="proctoringTypeId"),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> ProctoringTypeItemSchema:
    return await proctoring_service.get_proctoring_type_by_id(
        user=user, proctoring_type_id=proctoring_type_id
    )


@router.patch("/proctoringType/{proctoringTypeId}", status_code=status.HTTP_200_OK)
async def update_proctoring_type(
    proctoring_type_data: UpdateProctoringTypeSchema,
    proctoring_type_id: int = Path(alias="proctoringTypeId"),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.update_proctoring_type(
        user=user,
        proctoring_type_id=proctoring_type_id,
        proctoring_type_data=proctoring_type_data,
    )


@router.delete("/proctoringType/{proctoringTypeId}", status_code=status.HTTP_200_OK)
async def delete_proctoring_type(
    proctoring_type_id: int = Path(alias="proctoringTypeId"),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.delete_proctoring_type(
        user=user, proctoring_type_id=proctoring_type_id
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_proctoring(
    proctoring_data: CreateProctoringSchema,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.create_proctoring(
        user=user, proctoring_data=proctoring_data
    )


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_proctoring(
    filters: ProctoringFilters = Depends(),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[ProctoringItemSchema]:
    return await proctoring_service.get_list_of_proctoring(user=user, filters=filters)


@router.get("/{proctoringId}", status_code=status.HTTP_200_OK)
async def get_proctoring_by_id(
    proctoring_id: int = Path(alias="proctoringId"),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> ProctoringItemSchema:
    return await proctoring_service.get_proctoring_by_id(
        user=user, proctoring_id=proctoring_id
    )


@router.patch("/{proctoringId}", status_code=status.HTTP_200_OK)
async def patch_proctoring(
    proctoring_data: PatchProctoringSchema,
    proctoring_id: int,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await proctoring_service.update_proctoring(
        user=user, proctoring_id=proctoring_id, proctoring_data=proctoring_data
    )


@router.delete("/{proctoringId}", status_code=status.HTTP_200_OK)
async def delete_proctoring(
    proctoring_id: int,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    return await proctoring_service.delete_proctoring_by_id(
        user=user, proctoring_id=proctoring_id
    )


@router.post("/upload-sample", status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_moodle_token)])
async def upload_sample(
    sample_data: SampleData,
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
):
    return await proctoring_service.upload_sample(sample_data=sample_data)



@router.post("/check", status_code=status.HTTP_200_OK, dependencies=[Depends(check_moodle_token)])
async def check_image(
    image: UploadFile,
    proctoring_id: int = Query(alias="proctoringId"),
    proctoring_service: ProctoringService = Depends(proctoring_service_dependency),
) -> None:

    return await proctoring_service.check_image(
        proctoring_id=proctoring_id,
        image=image,
    )
