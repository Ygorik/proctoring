"""DB сервис для работы со снимками прокторинга"""
from datetime import datetime

from sqlalchemy import select, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base_db_service import BaseDBService
from src.db.models.snapshot_model import ProctoringSnapshotDB
from src.services.snapshot.schemas import SnapshotCreateSchema, SnapshotFilters


class SnapshotDBService(BaseDBService):
    """Сервис для работы с БД снимков"""
    
    async def insert_snapshot(
        self,
        *,
        proctoring_id: int,
        bucket_name: str,
        object_key: str,
        file_size: int,
        content_type: str,
        timestamp: datetime,
        violation_type: str | None = None,
        violation_severity: str | None = None,
        description: str | None = None,
        is_violation: bool = False,
        metadata_json: dict | None = None
    ) -> ProctoringSnapshotDB:
        """Создает новый снимок в БД"""
        async with self.get_async_session() as sess:
            stmt = insert(ProctoringSnapshotDB).values(
                proctoring_id=proctoring_id,
                bucket_name=bucket_name,
                object_key=object_key,
                file_size=file_size,
                content_type=content_type,
                timestamp=timestamp,
                uploaded_at=datetime.now(),
                violation_type=violation_type,
                violation_severity=violation_severity,
                description=description,
                is_violation=is_violation,
                metadata_json=metadata_json
            ).returning(ProctoringSnapshotDB)
            
            result = await sess.execute(stmt)
            await sess.commit()
            return result.scalar_one()
    
    async def get_snapshot_by_id(self, *, snapshot_id: int) -> ProctoringSnapshotDB | None:
        """Получает снимок по ID"""
        async with self.get_async_session() as sess:
            return await sess.scalar(
                select(ProctoringSnapshotDB).where(ProctoringSnapshotDB.id == snapshot_id)
            )
    
    async def get_snapshots_by_proctoring_id(
        self, *, proctoring_id: int
    ) -> list[ProctoringSnapshotDB]:
        """Получает все снимки для сессии прокторинга"""
        async with self.get_async_session() as sess:
            result = await sess.execute(
                select(ProctoringSnapshotDB)
                .where(ProctoringSnapshotDB.proctoring_id == proctoring_id)
                .order_by(ProctoringSnapshotDB.timestamp)
            )
            return result.scalars().all()
    
    async def get_snapshots_with_filters(
        self, *, filters: SnapshotFilters
    ) -> list[ProctoringSnapshotDB]:
        """Получает снимки с фильтрацией"""
        async with self.get_async_session() as sess:
            conditions = []
            
            if filters.proctoring_id is not None:
                conditions.append(ProctoringSnapshotDB.proctoring_id == filters.proctoring_id)
            
            if filters.is_violation is not None:
                conditions.append(ProctoringSnapshotDB.is_violation == filters.is_violation)
            
            if filters.violation_type is not None:
                conditions.append(ProctoringSnapshotDB.violation_type == filters.violation_type)
            
            if filters.date_from is not None:
                conditions.append(ProctoringSnapshotDB.timestamp >= filters.date_from)
            
            if filters.date_to is not None:
                conditions.append(ProctoringSnapshotDB.timestamp <= filters.date_to)
            
            stmt = select(ProctoringSnapshotDB).order_by(ProctoringSnapshotDB.timestamp)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await sess.execute(stmt)
            return result.scalars().all()
    
    async def delete_snapshot(self, *, snapshot_id: int) -> None:
        """Удаляет снимок из БД"""
        async with self.get_async_session() as sess:
            await sess.execute(
                delete(ProctoringSnapshotDB).where(ProctoringSnapshotDB.id == snapshot_id)
            )
            await sess.commit()
    
    async def delete_snapshots_by_proctoring_id(self, *, proctoring_id: int) -> None:
        """Удаляет все снимки для сессии прокторинга"""
        async with self.get_async_session() as sess:
            await sess.execute(
                delete(ProctoringSnapshotDB).where(
                    ProctoringSnapshotDB.proctoring_id == proctoring_id
                )
            )
            await sess.commit()
