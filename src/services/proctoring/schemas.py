from fastapi import Query

from src.base_schemas import BaseResponseSchemas


class CreateProctoringSchema(BaseResponseSchemas):
    user_id: int
    subject_id: int
    type_id: int


class CreateProctoringTypeSchema(BaseResponseSchemas):
    name: str
    absence_person: bool
    extra_person: bool
    person_substitution: bool
    looking_away: bool
    mouth_opening: bool
    hints_outside: bool


class ProctoringTypeItemSchema(BaseResponseSchemas):
    name: str
    absence_person: bool
    extra_person: bool
    person_substitution: bool
    looking_away: bool
    mouth_opening: bool
    hints_outside: bool


class UpdateProctoringTypeSchema(BaseResponseSchemas):
    name: str
    absence_person: bool
    extra_person: bool
    person_substitution: bool
    looking_away: bool
    mouth_opening: bool
    hints_outside: bool


class ProctoringItemSchema(BaseResponseSchemas):
    proctoring_name: str
    user_name: str
    subject_name: str


class PatchProctoringSchema(BaseResponseSchemas):
    user_id: int
    subject_id: int
    type_id: int


class ProctoringFilters:
    def __init__(
        self,
        user_id: int | None = Query(default=None, alias="userId"),
        subject_id: int | None = Query(default=None, alias="subjectId"),
        type_id: int | None = Query(default=None, alias="typeId"),
    ):
        self.user_id = user_id
        self.subject_id = subject_id
        self.type_id = type_id
