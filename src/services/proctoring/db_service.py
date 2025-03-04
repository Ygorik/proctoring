from sqlalchemy import insert, select

from src.db.base_db_service import BaseDBService
from src.db.models import ProctoringDB
from src.services.proctoring.schemas import CreateProctoringSchema, ProctoringItemSchema


class ProctoringDBService(BaseDBService):
    async def insert_proctoring(self, *, proctoring_data: CreateProctoringSchema):
        async with self.get_async_session() as sess:
            await sess.execute(insert(ProctoringDB).values(proctoring_data.model_dump()))
            await sess.commit()

    async def get_list_of_proctoring(self) -> list[ProctoringItemSchema]:
        async with self.get_async_session() as sess:
            return await sess.scalars(select(ProctoringDB))

    async def get_proctoring_by_id(self, *, proctoring_id: int) -> ProctoringItemSchema:
        async with self.get_async_session() as sess:
            return await sess.scalar(select(ProctoringDB).where(ProctoringDB.id == proctoring_id))
