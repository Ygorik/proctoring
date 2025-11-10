from src.services.subject.db_service import SubjectDBService
from src.services.subject.exceptions import SubjectNotFoundError
from src.services.subject.schemas import (
    CreateSubjectSchema,
    SubjectSchema,
    SubjectListItemSchema,
    PatchSubjectSchema,
    AssignSubjectSchema,
    UnassignSubjectSchema,
    AssignedSubjectSchema,
    SubjectFilters,
)
from src.services.user.service import UserService

from src.utils.role_checker import (
    check_create_rights,
    check_read_rights,
    check_update_rights,
    check_delete_rights,
)


class SubjectService:
    def __init__(
        self, *, subject_db_service: SubjectDBService, user_service: UserService
    ) -> None:
        self.subject_db_service = subject_db_service
        self.user_service = user_service

    @check_create_rights
    async def create_subject(self, *, subject_data: CreateSubjectSchema) -> None:
        await self.subject_db_service.insert_subject(subject_data=subject_data)

    @check_read_rights
    async def get_subject_by_id(self, *, subject_id: int) -> SubjectSchema:
        return await self.get_subject_by_id_if_exist(subject_id=subject_id)

    async def get_subject_by_id_if_exist(self, *, subject_id) -> SubjectSchema:
        if subject := await self.subject_db_service.get_subject_by_id(
            subject_id=subject_id
        ):
            return subject
        raise SubjectNotFoundError

    @check_read_rights
    async def get_list_of_subjects(
        self, *, filters: SubjectFilters
    ) -> list[SubjectListItemSchema]:
        return await self.subject_db_service.get_list_of_subjects(filters=filters)

    @check_update_rights
    async def patch_subject_by_id(
        self, *, subject_data: PatchSubjectSchema, subject_id: int
    ) -> None:
        await self.get_subject_by_id_if_exist(subject_id=subject_id)
        await self.subject_db_service.update_subject(
            subject_data=subject_data, subject_id=subject_id
        )

    @check_delete_rights
    async def delete_subject_by_id(self, *, subject_id: int) -> None:
        await self.get_subject_by_id_if_exist(subject_id=subject_id)
        await self.subject_db_service.delete_subject_by_id(subject_id=subject_id)

    @check_create_rights
    async def assign_subject_to_user(self, *, assign_data: AssignSubjectSchema) -> None:
        await self.get_subject_by_id_if_exist(subject_id=assign_data.subject_id)
        await self.user_service.get_user_by_id_if_exist(user_id=assign_data.user_id)

        await self.subject_db_service.assign_subject_to_user(assign_data=assign_data)

    @check_delete_rights
    async def unassign_subject_from_user(
        self, *, unassign_data: UnassignSubjectSchema
    ) -> None:
        await self.subject_db_service.unassign_subject_from_user(
            unassign_data=unassign_data
        )

    @check_read_rights
    async def get_assigned_subjects(
        self, *, subject_id: int | None = None, user_id: str | None = None
    ) -> list[AssignedSubjectSchema]:
        return await self.subject_db_service.get_assigned_subjects(
            subject_id=subject_id, user_id=user_id
        )
