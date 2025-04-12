from fastapi import APIRouter, Depends, Path
from starlette import status

from src.services.authorization.schemas import User
from src.services.subject.dependencies import subject_service_dependency
from src.services.subject.schemas import (
    CreateSubjectSchema,
    SubjectSchema,
    SubjectListItemSchema,
    PatchSubjectSchema,
    AssignSubjectSchema,
    UnassignSubjectSchema,
    SubjectFilters,
)
from src.services.subject.service import SubjectService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: CreateSubjectSchema,
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await service.create_subject(user=user, subject_data=subject_data)


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_subjects(
    filters: SubjectFilters = Depends(),
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[SubjectListItemSchema]:
    return await service.get_list_of_subjects(user=user, filters=filters)


@router.patch("/{subject_id}", status_code=status.HTTP_200_OK)
async def patch_subject_by_id(
    subject_data: PatchSubjectSchema,
    subject_id: int = Path(alias="subjectId"),
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await service.patch_subject_by_id(
        user=user, subject_data=subject_data, subject_id=subject_id
    )


@router.post("/assignSubject", status_code=status.HTTP_201_CREATED)
async def assign_subject_to_user(
    assign_data: AssignSubjectSchema,
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await service.assign_subject_to_user(user=user, assign_data=assign_data)


@router.delete("/assignSubject", status_code=status.HTTP_201_CREATED)
async def unassign_subject_from_user(
    unassign_data: UnassignSubjectSchema,
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await service.unassign_subject_from_user(user=user, unassign_data=unassign_data)


@router.get("/{subject_id}", status_code=status.HTTP_200_OK)
async def get_subject(
    subject_id: int = Path(alias="subjectId"),
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> SubjectSchema:
    return await service.get_subject_by_id(user=user, subject_id=subject_id)


@router.delete("/{subject_id}", status_code=status.HTTP_200_OK)
async def delete_subject_by_id(
    subject_id: int = Path(alias="subjectId"),
    service: SubjectService = Depends(subject_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await service.delete_subject_by_id(user=user, subject_id=subject_id)
