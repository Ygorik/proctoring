from fastapi import APIRouter, Depends, Path
from starlette import status

from src.services.subject.dependencies import subject_service_dependency
from src.services.subject.schemas import CreateSubjectSchema, SubjectSchema, SubjectListItemSchema, PatchSubjectSchema
from src.services.subject.service import SubjectService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: CreateSubjectSchema,
    service: SubjectService = Depends(subject_service_dependency),
) -> None:
    await service.create_subject(subject_data=subject_data)


@router.get("/{subject_id}", status_code=status.HTTP_200_OK)
async def get_subject(
    subject_id: int = Path(),
    service: SubjectService = Depends(subject_service_dependency),
) -> SubjectSchema:
    return await service.get_subject_by_id(subject_id=subject_id)


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_subjects(
    service: SubjectService = Depends(subject_service_dependency),
) -> list[SubjectListItemSchema]:
    return await service.get_list_of_subjects()


@router.patch("/{subject_id}", status_code=status.HTTP_200_OK)
async def patch_subject_by_id(
    subject_data: PatchSubjectSchema,
    subject_id: int = Path(),
    service: SubjectService = Depends(subject_service_dependency),
) -> None:
    await service.patch_subject_by_id(subject_data=subject_data, subject_id=subject_id)


@router.delete("/{subject_id}", status_code=status.HTTP_200_OK)
async def delete_subject_by_id(
    subject_id: int = Path(),
    service: SubjectService = Depends(subject_service_dependency),
) -> None:
    await service.delete_subject_by_id(subject_id=subject_id)
