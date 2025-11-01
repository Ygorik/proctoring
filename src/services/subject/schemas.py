from fastapi import Query

from src.base_schemas import BaseResponseSchemas


class CreateSubjectSchema(BaseResponseSchemas):
    id: int | None = None
    name: str


class SubjectSchema(BaseResponseSchemas):
    id: int
    name: str


class SubjectListItemSchema(BaseResponseSchemas):
    id: int
    name: str


class PatchSubjectSchema(BaseResponseSchemas):
    name: str


class AssignSubjectSchema(BaseResponseSchemas):
    subject_id: int
    user_id: int


class UnassignSubjectSchema(BaseResponseSchemas):
    subject_id: int
    user_id: int


class SubjectFilters:
    def __init__(
        self,
        user_id: int | None = Query(default=None, alias="userId"),
    ):
        self.user_id = user_id
