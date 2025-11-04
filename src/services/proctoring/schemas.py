from fastapi import Query

from src.base_schemas import BaseResponseSchemas
from src.services.quiz.schemas import CreateQuizSchema
from src.services.subject.schemas import CreateSubjectSchema


class CreateProctoringSchema(BaseResponseSchemas):
    user_id: str
    subject_id: int
    type_id: int
    quiz_id: int
    attempt_id: int


class InsertProctoringSchema(CreateProctoringSchema):
    result_id: int


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
    result_id: int


class PatchProctoringSchema(BaseResponseSchemas):
    user_id: str
    subject_id: int
    type_id: int


class ProctoringFilters:
    def __init__(
        self,
        user_id: str | None = Query(default=None, alias="userId"),
        subject_id: int | None = Query(default=None, alias="subjectId"),
        type_id: int | None = Query(default=None, alias="typeId"),
    ):
        self.user_id = user_id
        self.subject_id = subject_id
        self.type_id = type_id


class SampleUser(BaseResponseSchemas):
    id: str
    full_name: str



class SampleData(BaseResponseSchemas):
    user: SampleUser
    subject: CreateSubjectSchema
    quiz: CreateQuizSchema
    type_id: int | None = None
    attempt: int
    preflight_id: int
