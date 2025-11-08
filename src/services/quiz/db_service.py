from typing import Sequence

from sqlalchemy import insert, select, update

from src.db.base_db_service import BaseDBService
from src.db.models import QuizDB
from src.services.quiz.schemas import CreateQuizSchema, PatchQuizSchema


class QuizDBService(BaseDBService):
    async def insert_quiz(self, quiz_data: CreateQuizSchema) -> int:
        async with self.get_async_session() as sess:
            await sess.execute(insert(QuizDB).values(**quiz_data.model_dump()))
            await sess.commit()
        return quiz_data.id

    async def get_list_of_quizs(self) -> Sequence[QuizDB]:
        async with self.get_async_session() as sess:
            return await sess.scalars(select(QuizDB))

    async def update_quiz(self, *, quiz_id: int, quiz_data: PatchQuizSchema) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(QuizDB)
                .values(**quiz_data.model_dump(exclude_unset=True))
                .where(QuizDB.id == quiz_id)
            )
            await sess.commit()

    async def get_quiz_by_id(self, *, quiz_id: int) -> QuizDB:
        async with self.get_async_session() as sess:
            return await sess.scalar(select(QuizDB).where(QuizDB.id == quiz_id))
