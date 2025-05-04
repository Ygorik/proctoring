from src.base_schemas import BaseResponseSchemas
from src.services.proctoring_result.schemas import PatchProctoringResultSchema


class ProctoringResultSchema(PatchProctoringResultSchema):
    ...


class ProctoringTypeSchema(BaseResponseSchemas):
    absence_person: bool
    extra_person: bool
    person_substitution: bool
    looking_away: bool
    mouth_opening: bool
    hints_outside: bool
