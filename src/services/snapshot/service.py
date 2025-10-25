"""Основной сервис для работы со снимками прокторинга"""
from datetime import datetime
from typing import BinaryIO

from fastapi import UploadFile

from src.services.snapshot.db_service import SnapshotDBService
from src.services.snapshot.minio_service import minio_service
from src.services.snapshot.pdf_report_service import pdf_report_service
from src.services.snapshot.schemas import (
    SnapshotItemSchema,
    SnapshotListSchema,
    SnapshotFilters,
)
from src.services.snapshot.exceptions import (
    SnapshotNotFoundError,
    SnapshotUploadError,
    InvalidImageFormatError,
)
from src.services.proctoring.db_service import ProctoringDBService
from src.services.proctoring.exceptions import ProctoringNotFoundError
from src.services.user.db_service import UserDBService
from src.services.authorization.exceptions import UserNotFoundError
from src.utils.role_checker import check_read_rights, check_create_rights, check_delete_rights


class SnapshotService:
    """Сервис для работы со снимками прокторинга"""
    
    def __init__(
        self,
        snapshot_db_service: SnapshotDBService,
        proctoring_db_service: ProctoringDBService,
        user_db_service: UserDBService,
    ):
        self.snapshot_db_service = snapshot_db_service
        self.proctoring_db_service = proctoring_db_service
        self.user_db_service = user_db_service
    
    @check_read_rights
    async def get_snapshots_by_proctoring_id(
        self, *, proctoring_id: int
    ) -> SnapshotListSchema:
        """Получает все снимки для сессии прокторинга"""
        # Проверяем существование сессии
        if not await self.proctoring_db_service.get_proctoring_by_id(
            proctoring_id=proctoring_id
        ):
            raise ProctoringNotFoundError
        
        # Получаем снимки
        snapshots = await self.snapshot_db_service.get_snapshots_by_proctoring_id(
            proctoring_id=proctoring_id
        )
        
        # Формируем ответ
        snapshot_items = [
            SnapshotItemSchema.model_validate(snapshot) for snapshot in snapshots
        ]
        
        violations_count = sum(1 for s in snapshots if s.is_violation)
        
        return SnapshotListSchema(
            snapshots=snapshot_items,
            total_count=len(snapshots),
            violations_count=violations_count
        )
    
    @check_read_rights
    async def get_snapshot_by_id(self, *, snapshot_id: int) -> SnapshotItemSchema:
        """Получает снимок по ID"""
        snapshot = await self.snapshot_db_service.get_snapshot_by_id(
            snapshot_id=snapshot_id
        )
        
        if not snapshot:
            raise SnapshotNotFoundError
        
        return SnapshotItemSchema.model_validate(snapshot)
    
    @check_create_rights
    async def upload_snapshot(
        self,
        *,
        proctoring_id: int,
        image: UploadFile,
        violation_type: str | None = None,
        violation_severity: str | None = None,
        description: str | None = None,
    ) -> SnapshotItemSchema:
        """Загружает новый снимок"""
        # Проверяем формат файла
        if not image.content_type or not image.content_type.startswith("image/"):
            raise InvalidImageFormatError
        
        # Проверяем существование сессии прокторинга
        proctoring = await self.proctoring_db_service.get_proctoring_by_id(
            proctoring_id=proctoring_id
        )
        if not proctoring:
            raise ProctoringNotFoundError
        
        # Читаем байты изображения
        image_bytes = await image.read()
        timestamp = datetime.now()
        
        # Генерируем ключ для MinIO
        object_key = minio_service.generate_object_key(
            user_id=proctoring.user_id,
            proctoring_id=proctoring_id,
            timestamp=timestamp,
            violation_type=violation_type
        )
        
        # Загружаем в MinIO
        try:
            object_key, file_size = minio_service.upload_snapshot(
                file_data=image_bytes,
                object_key=object_key,
                content_type=image.content_type
            )
        except Exception as e:
            raise SnapshotUploadError(f"Failed to upload to MinIO: {str(e)}")
        
        # Сохраняем метаданные в БД
        is_violation = violation_type is not None
        
        snapshot = await self.snapshot_db_service.insert_snapshot(
            proctoring_id=proctoring_id,
            bucket_name=minio_service.bucket_name,
            object_key=object_key,
            file_size=file_size,
            content_type=image.content_type,
            timestamp=timestamp,
            violation_type=violation_type,
            violation_severity=violation_severity,
            description=description,
            is_violation=is_violation,
            metadata_json={
                "user_id": proctoring.user_id,
                "original_filename": image.filename,
            }
        )
        
        return SnapshotItemSchema.model_validate(snapshot)
    
    @check_delete_rights
    async def delete_snapshot(self, *, snapshot_id: int) -> None:
        """Удаляет снимок"""
        snapshot = await self.snapshot_db_service.get_snapshot_by_id(
            snapshot_id=snapshot_id
        )
        
        if not snapshot:
            raise SnapshotNotFoundError
        
        # Удаляем из MinIO
        try:
            minio_service.delete_snapshot(snapshot.object_key)
        except Exception as e:
            # Логируем ошибку, но продолжаем удаление из БД
            print(f"Warning: Failed to delete from MinIO: {str(e)}")
        
        # Удаляем из БД
        await self.snapshot_db_service.delete_snapshot(snapshot_id=snapshot_id)
    
    @check_read_rights
    async def generate_pdf_report(self, *, proctoring_id: int) -> BinaryIO:
        """Генерирует PDF отчет по сессии прокторинга"""
        # Проверяем существование сессии
        if not await self.proctoring_db_service.get_proctoring_by_id(
            proctoring_id=proctoring_id
        ):
            raise ProctoringNotFoundError
        
        # Генерируем отчет
        return await pdf_report_service.generate_report(
            proctoring_id=proctoring_id,
            session=self.snapshot_db_service.session
        )
