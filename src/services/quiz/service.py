from src.services.quiz.db_service import QuizDBService
from src.services.quiz.exceptions import QuizNotFoundError
from src.services.quiz.schemas import PatchQuizSchema, QuizItemSchema
from src.utils.role_checker import (
    check_read_rights,
    check_delete_rights,
    check_update_rights,
    check_create_rights,
)


class QuizService:
    def __init__(self, *, quiz_db_service: QuizDBService) -> None:
        self.quiz_db_service = quiz_db_service

    @check_read_rights
    async def get_list_of_qiuz(self) -> list[QuizItemSchema]:
        return [
            QuizItemSchema.model_validate(quiz)
            for quiz in await self.quiz_db_service.get_list_of_quizs()
        ]

    @check_read_rights
    async def get_quiz_by_id(self, *, quiz_id: int) -> QuizItemSchema:
        return await self.get_quiz_by_id_if_exist(quiz_id=quiz_id)

    @check_update_rights
    async def update_quiz(self, *, quiz_id: int, quiz_data: PatchQuizSchema) -> None:
        await self.get_quiz_by_id_if_exist(quiz_id=quiz_id)
        await self.quiz_db_service.update_quiz(quiz_id=quiz_id, quiz_data=quiz_data)

    async def get_quiz_by_id_if_exist(self, *, quiz_id: int) -> QuizItemSchema:
        if quiz := await self.quiz_db_service.get_quiz_by_id(quiz_id=quiz_id):
            return QuizItemSchema.model_validate(quiz)
        raise QuizNotFoundError
