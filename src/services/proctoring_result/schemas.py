from src.base_schemas import BaseResponseSchemas


class ProctoringResultFilters(BaseResponseSchemas):
    subject_name: str | None = None
    user_name: str | None = None
    proctoring_type_name: str | None = None
    proctoring_id: int | None = None


class ProctoringResultItemSchema(BaseResponseSchemas):
    id: int
    user_name: str
    subject_name: str
    proctoring_name: str
    detected_absence_person: bool
    detected_extra_person: bool
    detected_person_substitution: bool
    detected_looking_away: bool
    detected_mouth_opening: bool
    detected_hints_outside: bool


class PatchProctoringResultSchema(BaseResponseSchemas):
    detected_absence_person: bool | None
    detected_extra_person: bool | None
    detected_person_substitution: bool | None
    detected_looking_away: bool | None
    detected_mouth_opening: bool | None
    detected_hints_outside: bool | None
