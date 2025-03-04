from src.services.proctoring.db_service import ProctoringDBService
from src.services.proctoring.exceptions import ProctoringNotFoundError
from src.services.proctoring.schemas import ProctoringItemSchema, CreateProctoringSchema, PatchProctoringSchema

from src.utils.role_checker import (
    check_read_rights,
    check_delete_rights,
    check_update_rights,
    check_create_rights,
)


class ProctoringService:
    def __init__(self, *, proctoring_db_service: ProctoringDBService) -> None:
        self.proctoring_db_service = proctoring_db_service

    @check_create_rights
    async def create_proctoring(self, *, proctoring_data: CreateProctoringSchema):
        await self.proctoring_db_service.insert_proctoring(proctoring_data=proctoring_data)

    @check_read_rights
    async def get_list_of_proctoring(self) -> list[ProctoringItemSchema]:
        await self.proctoring_db_service.get_list_of_proctoring()

    @check_read_rights
    async def get_proctoring_by_id(self, *, proctoring_id: int):
        return await self.get_proctoring_by_id_if_exist(proctoring_id=proctoring_id)

    @check_update_rights
    async def update_proctoring(self, *, proctoring_id: int, proctoring_data: PatchProctoringSchema):
        await self.get_proctoring_by_id_if_exist(proctoring_id=proctoring_id)

    @check_delete_rights
    async def delete_proctoring_by_id(self, *, proctoring_id: int):
        await self.get_proctoring_by_id_if_exist(proctoring_id=proctoring_id)

    async def get_proctoring_by_id_if_exist(self, *, proctoring_id) -> ProctoringItemSchema:
        if proctoring := await self.proctoring_db_service.get_proctoring_by_id(proctoring_id=proctoring_id):
            return ProctoringItemSchema.model_validate(proctoring)
        raise ProctoringNotFoundError
