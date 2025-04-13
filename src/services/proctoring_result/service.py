from src.services.proctoring_result.db_service import ProctoringResultDBService
from src.services.proctoring_result.exceptions import ProctoringResultNotFoundError
from src.services.proctoring_result.schemas import (
    ProctoringResultFilters,
    ProctoringResultItemSchema,
    PatchProctoringResultSchema,
)
from src.utils.role_checker import (
    check_read_rights,
    check_update_rights,
    check_delete_rights,
)


class ProctoringResultService:
    def __init__(
        self, *, proctoring_result_db_service: ProctoringResultDBService
    ) -> None:
        self.proctoring_result_db_service = proctoring_result_db_service

    @check_read_rights
    async def get_proctoring_result_list(
        self, *, filters: ProctoringResultFilters
    ) -> list[ProctoringResultItemSchema]:
        return [
            ProctoringResultItemSchema(
                id=proctoring.proctoring_result.id,
                user_name=proctoring.user.full_name,
                subject_name=proctoring.subject.name,
                proctoring_name=proctoring.proctoring_type.name,
                detected_absence_person=proctoring.proctoring_result.detected_absence_person,
                detected_extra_person=proctoring.proctoring_result.detected_extra_person,
                detected_person_substitution=proctoring.proctoring_result.detected_person_substitution,
                detected_looking_away=proctoring.proctoring_result.detected_looking_away,
                detected_mouth_opening=proctoring.proctoring_result.detected_mouth_opening,
                detected_hints_outside=proctoring.proctoring_result.detected_hints_outside,
            )
            for proctoring in await self.proctoring_result_db_service.get_proctoring_list_with_result(
                filters=filters
            )
        ]

    @check_read_rights
    async def get_proctoring_result_by_id(
        self, *, proctoring_result_id: int
    ) -> ProctoringResultItemSchema:
        return await self.get_proctoring_result_by_id_if_exist(
            result_id=proctoring_result_id
        )

    async def get_proctoring_result_by_id_if_exist(
        self, *, result_id
    ) -> ProctoringResultItemSchema:
        if proctoring := await self.proctoring_result_db_service.get_proctoring_with_result_by_result_id(
            result_id=result_id
        ):
            return ProctoringResultItemSchema(
                id=proctoring.proctoring_result.id,
                user_name=proctoring.user.full_name,
                subject_name=proctoring.subject.name,
                proctoring_name=proctoring.proctoring_type.name,
                detected_absence_person=proctoring.proctoring_result.detected_absence_person,
                detected_extra_person=proctoring.proctoring_result.detected_extra_person,
                detected_person_substitution=proctoring.proctoring_result.detected_person_substitution,
                detected_looking_away=proctoring.proctoring_result.detected_looking_away,
                detected_mouth_opening=proctoring.proctoring_result.detected_mouth_opening,
                detected_hints_outside=proctoring.proctoring_result.detected_hints_outside,
            )
        raise ProctoringResultNotFoundError

    @check_update_rights
    async def update_proctoring_result(
        self,
        *,
        proctoring_result_id: int,
        proctoring_result_data: PatchProctoringResultSchema,
    ) -> None:
        await self.get_proctoring_result_by_id_if_exist(
            result_id=proctoring_result_id
        )
        await self.proctoring_result_db_service.update_proctoring_result(
            proctoring_result_id=proctoring_result_id,
            proctoring_result_data=proctoring_result_data,
        )

    @check_delete_rights
    async def delete_proctoring_result(self, *, proctoring_result_id) -> None:
        await self.get_proctoring_result_by_id_if_exist(
            result_id=proctoring_result_id
        )
        await self.proctoring_result_db_service.delete_proctoring_result(
            proctoring_result_id=proctoring_result_id
        )
