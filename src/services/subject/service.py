from src.services.subject.db_service import SubjectDBService
from src.services.subject.exceptions import SubjectNotFoundError
from src.services.subject.schemas import CreateSubjectSchema, SubjectSchema, SubjectListItemSchema, PatchSubjectSchema


class SubjectService:
    def __init__(self, *, subject_db_service: SubjectDBService) -> None:
        self.subject_db_service = subject_db_service

    async def create_subject(self, *, subject_data: CreateSubjectSchema) -> None:
        await self.subject_db_service.insert_subject(subject_data=subject_data)

    async def get_subject_by_id(self, *, subject_id: int) -> SubjectSchema:
        return await self.get_subject_by_id_if_exist(subject_id=subject_id)

    async def get_subject_by_id_if_exist(self, *, subject_id) -> SubjectSchema:
        if subject := await self.subject_db_service.get_subject_by_id(subject_id=subject_id):
            return subject
        raise SubjectNotFoundError

    async def get_list_of_subjects(self) -> list[SubjectListItemSchema]:
        return await self.subject_db_service.get_list_of_subjects()

    async def patch_subject_by_id(self, *, subject_data: PatchSubjectSchema, subject_id: int) -> None:
        await self.get_subject_by_id_if_exist(subject_id=subject_id)
        await self.subject_db_service.update_subject(subject_data=subject_data, subject_id=subject_id)

    async def delete_subject_by_id(self, *, subject_id: int) -> None:
        await self.get_subject_by_id_if_exist(subject_id=subject_id)
        await self.subject_db_service.delete_subject_by_id(subject_id=subject_id)
