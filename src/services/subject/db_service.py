from sqlalchemy import insert, select, update, delete

from src.db.base_db_service import BaseDBService
from src.db.models import SubjectDB, SubjectUserDB
from src.services.subject.schemas import (
    CreateSubjectSchema,
    SubjectSchema,
    SubjectListItemSchema,
    PatchSubjectSchema,
    AssignSubjectSchema,
    UnassignSubjectSchema,
)


class SubjectDBService(BaseDBService):
    async def insert_subject(self, *, subject_data: CreateSubjectSchema) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(insert(SubjectDB).values(**subject_data.model_dump()))
            await sess.commit()

    async def get_subject_by_id(self, *, subject_id: int) -> SubjectSchema:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(SubjectDB).where(SubjectDB.id == subject_id)
            )

    async def get_list_of_subjects(self) -> list[SubjectListItemSchema]:
        async with self.get_async_session() as sess:
            return await sess.scalars(select(SubjectDB))

    async def update_subject(
        self, *, subject_data: PatchSubjectSchema, subject_id: int
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(SubjectDB)
                .values(**subject_data.model_dump())
                .where(SubjectDB.id == subject_id)
            )
            await sess.commit()

    async def delete_subject_by_id(self, *, subject_id: int) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(delete(SubjectDB).where(SubjectDB.id == subject_id))
            await sess.commit()

    async def assign_subject_to_user(self, *, assign_data: AssignSubjectSchema) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(insert(SubjectUserDB).values(**assign_data.model_dump()))
            await sess.commit()

    async def unassign_subject_from_user(
        self, *, unassign_data: UnassignSubjectSchema
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                delete(SubjectUserDB).where(
                    SubjectUserDB.user_id == unassign_data.user_id,
                    SubjectUserDB.subject_id == unassign_data.subject_id,
                )
            )
            await sess.commit()

    async def get_user_subjects(self, *, user_id: str) -> list[SubjectListItemSchema]:
        async with self.get_async_session() as sess:
            return await sess.scalars(
                select(SubjectDB)
                .join(SubjectUserDB, SubjectUserDB.subject_id == SubjectDB.id)
                .where(SubjectUserDB.user_id == user_id)
            )
