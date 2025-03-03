from src.base_schemas import BaseResponseSchemas


class CreateSubjectSchema(BaseResponseSchemas):
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
    user_id: str


class UnassignSubjectSchema(BaseResponseSchemas):
    subject_id: int
    user_id: str
