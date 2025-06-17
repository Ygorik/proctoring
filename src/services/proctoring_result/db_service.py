from sqlalchemy import Select, select, update, delete
from sqlalchemy.orm import selectinload

from src.db.base_db_service import BaseDBService
from src.db.models import (
    ProctoringResultDB,
    ProctoringDB,
    ProctoringTypeDB,
    SubjectDB,
    UserDB,
)
from src.services.proctoring_result.schemas import (
    ProctoringResultFilters,
    ProctoringResultItemSchema,
    PatchProctoringResultSchema,
)


class ProctoringResultDBService(BaseDBService):
    async def get_proctoring_list_with_result(
        self, *, filters: ProctoringResultFilters
    ) -> list[ProctoringDB]:
        async with self.get_async_session() as sess:
            stmt = (
                select(ProctoringDB)
                .join(
                    ProctoringResultDB, ProctoringDB.result_id == ProctoringResultDB.id
                )
                .join(ProctoringTypeDB, ProctoringDB.type_id == ProctoringTypeDB.id)
                .join(SubjectDB, ProctoringDB.subject_id == SubjectDB.id)
                .join(UserDB, ProctoringDB.user_id == UserDB.id)
                .options(
                    selectinload(ProctoringDB.proctoring_result),
                    selectinload(ProctoringDB.subject),
                    selectinload(ProctoringDB.user),
                    selectinload(ProctoringDB.proctoring_type),
                )
            )
            stmt = await self.filter_proctoring_result_list(stmt=stmt, filters=filters)

            return await sess.scalars(stmt)

    @staticmethod
    async def filter_proctoring_result_list(
        *, stmt: Select, filters: ProctoringResultFilters
    ) -> Select:
        if filters.proctoring_id:
            stmt = stmt.where(ProctoringDB.id == filters.proctoring_id)
        if filters.proctoring_type_name:
            stmt = stmt.where(
                ProctoringTypeDB.name.icontains(filters.proctoring_type_name)
            )
        if filters.subject_name:
            stmt = stmt.where(SubjectDB.name.icontains(filters.subject_name))
        if filters.user_name:
            stmt = stmt.where(UserDB.full_name.icontains(filters.user_name))

        return stmt

    async def get_proctoring_with_result_by_result_id(
        self, *, result_id: int
    ) -> ProctoringResultItemSchema | None:
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(ProctoringDB)
                .join(
                    ProctoringResultDB, ProctoringDB.result_id == ProctoringResultDB.id
                )
                .join(ProctoringTypeDB, ProctoringDB.type_id == ProctoringTypeDB.id)
                .join(SubjectDB, ProctoringDB.subject_id == SubjectDB.id)
                .join(UserDB, ProctoringDB.user_id == UserDB.id)
                .options(
                    selectinload(ProctoringDB.proctoring_result),
                    selectinload(ProctoringDB.subject),
                    selectinload(ProctoringDB.user),
                    selectinload(ProctoringDB.proctoring_type),
                )
                .where(ProctoringResultDB.id == result_id)
            )

    async def update_proctoring_result(
        self,
        *,
        proctoring_result_id: int,
        proctoring_result_data: PatchProctoringResultSchema
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(ProctoringResultDB)
                .values(**proctoring_result_data.dict())
                .where(ProctoringResultDB.id == proctoring_result_id)
            )
            await sess.commit()

    async def set_new_proctoring_result(
        self,
        *,
        proctoring_result_id: int,
        proctoring_result_data: dict
    ) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(ProctoringResultDB)
                .values(**proctoring_result_data)
                .where(ProctoringResultDB.id == proctoring_result_id)
            )
            await sess.commit()

    async def delete_proctoring_result(self, *, proctoring_result_id: int) -> None:
        async with self.get_async_session() as sess:
            await sess.execute(
                update(ProctoringDB)
                .values(result_id=None)
                .where(ProctoringDB.result_id == proctoring_result_id)
            )

            await sess.execute(
                delete(ProctoringResultDB).where(
                    ProctoringResultDB.id == proctoring_result_id
                )
            )
            await sess.commit()
