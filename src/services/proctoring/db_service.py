from sqlalchemy import insert, select, update, delete, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.base_db_service import BaseDBService
from src.db.models import ProctoringDB, ProctoringTypeDB, ProctoringResultDB
from src.services.proctoring.schemas import (
    CreateProctoringSchema,
    ProctoringItemSchema,
    PatchProctoringSchema,
    CreateProctoringTypeSchema,
    ProctoringTypeItemSchema,
    UpdateProctoringTypeSchema,
    ProctoringFilters, 
    InsertProctoringSchema,
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

    async def get_list_of_proctoring_types(self) -> list[ProctoringTypeDB]:
        async with self.get_async_session() as sess:
            result = await sess.scalars(select(ProctoringTypeDB))
            return result.all()

    async def get_proctoring_type_by_id(
        self, *, proctoring_type_id: int
    ) -> ProctoringTypeDB | None:
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

    async def create_proctoring(
        self, *, proctoring_data: CreateProctoringSchema
    ) -> int:
        async with self.get_async_session() as sess:
            proctoring_result_id = await self.insert_proctoring_result(sess=sess)
            insert_proctoring_data = InsertProctoringSchema(
                **proctoring_data.model_dump(),
                result_id=proctoring_result_id,
            )
            proctoring_id = await self.insert_proctoring(sess=sess, proctoring_data=insert_proctoring_data)
            await sess.commit()
        return proctoring_id

    @staticmethod
    async def insert_proctoring_result(*, sess: AsyncSession) -> int:
        return await sess.scalar(
            insert(ProctoringResultDB).returning(ProctoringResultDB.id)
        )

    @staticmethod
    async def insert_proctoring(*, sess: AsyncSession, proctoring_data: InsertProctoringSchema) -> int:
        return await sess.scalar(
            insert(ProctoringDB).values(proctoring_data.model_dump()).returning(ProctoringDB.id)
        )

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

    async def get_proctoring_by_id(self, *, proctoring_id: int) -> ProctoringDB:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(ProctoringDB)
                .options(
                    selectinload(ProctoringDB.proctoring_type),
                    selectinload(ProctoringDB.user),
                    selectinload(ProctoringDB.subject),
                    selectinload(ProctoringDB.proctoring_result)
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

    async def get_default_proctoring_type_id(self) -> int | None:
        async with self.get_async_session() as sess:
            return await sess.scalar(select(ProctoringTypeDB.id).where(ProctoringTypeDB.default.is_(True)))
