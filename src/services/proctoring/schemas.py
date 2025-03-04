from src.base_schemas import BaseResponseSchemas


class CreateProctoringSchema(BaseResponseSchemas):
    user_id: int
    subject_id: int
    type_id: int


class ProctoringItemSchema(BaseResponseSchemas):
    proctoring_name: str
    user_name: str
    subject_name: str


class PatchProctoringSchema(BaseResponseSchemas):
    user_id: int
    subject_id: int
    type_id: int
