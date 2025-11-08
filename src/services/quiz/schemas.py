from src.base_schemas import BaseResponseSchemas

class CreateQuizSchema(BaseResponseSchemas):
    id: int
    name: str


class PatchQuizSchema(BaseResponseSchemas):
    name: str | None = None


class QuizItemSchema(BaseResponseSchemas):
    id: int
    name: str
