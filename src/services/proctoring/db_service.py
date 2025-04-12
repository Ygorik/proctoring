from sqlalchemy import insert, select, update, delete, Select
from sqlalchemy.orm import selectinload

from src.db.base_db_service import BaseDBService
from src.db.models import ProctoringDB, ProctoringTypeDB
from src.services.proctoring.schemas import (
    CreateProctoringSchema,
    ProctoringItemSchema,
    PatchProctoringSchema,
    CreateProctoringTypeSchema,
    ProctoringTypeItemSchema,
    UpdateProctoringTypeSchema,
    ProctoringFilters,
)


class ProctoringDBService(BaseDBService):
    async def insert_proctoring_type(
        self, *, proctoring_type_data: CreateProctoringTypeSchema
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                insert(ProctoringTypeDB).values(proctoring_type_data.model_dump())
            )
            await sess.commit()

    async def get_list_of_proctoring_types(self) -> list[ProctoringTypeItemSchema]:
        async with self.get_async_session() as sess:
            return await sess.scalars(select(ProctoringTypeDB))

    async def get_proctoring_type_by_id(
        self, *, proctoring_type_id: int
    ) -> ProctoringTypeItemSchema:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(ProctoringTypeDB).where(
                    ProctoringTypeDB.id == proctoring_type_id
                )
            )

    async def update_proctoring_type(
        self,
        *,
        proctoring_type_id: int,
        proctoring_type_data: UpdateProctoringTypeSchema
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(ProctoringTypeDB)
                .values(proctoring_type_data.model_dump())
                .where(ProctoringTypeDB.id == proctoring_type_id)
            )
            await sess.commit()

    async def delete_proctoring_type_by_id(self, *, proctoring_type_id: int) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                delete(ProctoringTypeDB).where(
                    ProctoringTypeDB.id == proctoring_type_id
                )
            )
            await sess.commit()

    async def insert_proctoring(
        self, *, proctoring_data: CreateProctoringSchema
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                insert(ProctoringDB).values(proctoring_data.model_dump())
            )
            await sess.commit()

    async def get_list_of_proctoring(
        self, *, filters: ProctoringFilters | None
    ) -> list[ProctoringDB]:
        stmt = select(ProctoringDB).options(
            selectinload(ProctoringDB.proctoring_type),
            selectinload(ProctoringDB.user),
            selectinload(ProctoringDB.subject),
        )

        stmt = self.filter_proctoring_list(stmt=stmt, filters=filters)

        async with self.get_async_session() as sess:
            return await sess.scalars(stmt)

    @staticmethod
    def filter_proctoring_list(*, stmt: Select, filters: ProctoringFilters) -> Select:
        if filters.type_id:
            stmt = stmt.where(ProctoringDB.type_id == filters.type_id)
        if filters.user_id:
            stmt = stmt.where(ProctoringDB.user_id == filters.user_id)
        if filters.subject_id:
            stmt = stmt.where(ProctoringDB.subject_id == filters.subject_id)

        return stmt

    async def get_proctoring_by_id(self, *, proctoring_id: int) -> ProctoringItemSchema:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(ProctoringDB)
                .options(
                    selectinload(ProctoringDB.proctoring_type),
                    selectinload(ProctoringDB.user),
                    selectinload(ProctoringDB.subject),
                )
                .where(ProctoringDB.id == proctoring_id)
            )

    async def update_proctoring(
        self, *, proctoring_id: int, proctoring_data: PatchProctoringSchema
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(ProctoringDB)
                .values(proctoring_data.model_dump())
                .where(ProctoringDB.id == proctoring_id)
            )
            await sess.commit()

    async def delete_proctoring_by_id(self, *, proctoring_id: int) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                delete(ProctoringDB).where(ProctoringDB.id == proctoring_id)
            )
            await sess.commit()
