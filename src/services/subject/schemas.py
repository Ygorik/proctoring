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
