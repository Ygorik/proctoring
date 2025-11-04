from fastapi import Depends

from src.db.base_db_service import Session
from src.services.quiz.db_service import QuizDBService
from src.services.quiz.service import QuizService


async def quiz_db_service_dependency() -> QuizDBService:
    return QuizDBService(Session)


async def quiz_service_dependency(
    quiz_db_service: QuizDBService = Depends(quiz_db_service_dependency),
) -> QuizService:
    return QuizService(quiz_db_service=quiz_db_service)
