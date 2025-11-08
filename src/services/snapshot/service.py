"""Основной сервис для работы со снимками прокторинга"""
from datetime import datetime
from typing import BinaryIO

from fastapi import UploadFile

from src.services.snapshot.db_service import SnapshotDBService
from src.services.snapshot.s3_service import s3_service
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
from src.utils.role_checker import check_read_rights, check_create_rights, check_delete_rights, check_update_rights


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
        
        return SnapshotListSchema(
            snapshots=snapshot_items,
            total_count=len(snapshots)
        )
    
    @check_read_rights
    async def get_snapshot_by_id(
        self, *, snapshot_id: int
    ) -> SnapshotItemSchema:
        """Получает снимок по ID"""
        snapshot = await self.snapshot_db_service.get_snapshot_by_id(
            snapshot_id=snapshot_id
        )
        
        if not snapshot:
            raise SnapshotNotFoundError()
        
        return SnapshotItemSchema.model_validate(snapshot)
    
    @check_create_rights
    async def create_snapshot(
        self,
        *,
        proctoring_id: int,
        image: UploadFile,
        violation_type: str | None = None,
        user_id: int,
    ) -> SnapshotItemSchema:
        if not image:
            raise InvalidImageFormatError()
        
        if not image.content_type or not image.content_type.startswith("image/"):
            raise InvalidImageFormatError()
        
        image_bytes = await image.read()
        timestamp = datetime.now()
        
        object_key = s3_service.generate_object_key(
            user_id=user_id,
            proctoring_id=proctoring_id or 0,
            timestamp=timestamp,
            violation_type=violation_type
        )
        
        try:
            object_key, _ = await s3_service.upload_snapshot(
                file_data=image_bytes,
                object_key=object_key,
                content_type=image.content_type
            )
        except Exception as e:
            raise SnapshotUploadError(message=f"Не удалось загрузить снимок: {str(e)}")
        
        snapshot = await self.snapshot_db_service.insert_snapshot(
            proctoring_id=proctoring_id,
            bucket_name=s3_service.bucket_name,
            object_key=object_key,
            violation_type=violation_type
        )
        
        return SnapshotItemSchema.model_validate(snapshot)
    
    @check_create_rights
    async def upload_snapshot(
        self,
        *,
        proctoring_id: int,
        image: UploadFile,
        violation_type: str | None = None,
    ) -> SnapshotItemSchema:
        """Загружает новый снимок нарушения"""
        # Проверяем формат файла
        if not image.content_type or not image.content_type.startswith("image/"):
            raise InvalidImageFormatError()
        
        # Проверяем существование сессии прокторинга
        proctoring = await self.proctoring_db_service.get_proctoring_by_id(
            proctoring_id=proctoring_id
        )
        if not proctoring:
            raise ProctoringNotFoundError
        
        # Читаем байты изображения
        image_bytes = await image.read()
        timestamp = datetime.now()
        
        # Генерируем ключ для S3
        object_key = s3_service.generate_object_key(
            user_id=proctoring.user_id,
            proctoring_id=proctoring_id,
            timestamp=timestamp,
            violation_type=violation_type
        )
        
        # Загружаем в S3 асинхронно
        try:
            object_key, _ = await s3_service.upload_snapshot(
                file_data=image_bytes,
                object_key=object_key,
                content_type=image.content_type
            )
        except Exception as e:
            raise SnapshotUploadError(message=f"Не удалось загрузить снимок: {str(e)}")
        
        # Сохраняем только ссылку на файл в БД
        snapshot = await self.snapshot_db_service.insert_snapshot(
            proctoring_id=proctoring_id,
            bucket_name=s3_service.bucket_name,
            object_key=object_key,
            violation_type=violation_type
        )
        
        return SnapshotItemSchema.model_validate(snapshot)
    
    @check_update_rights
    async def update_snapshot(
        self,
        *,
        snapshot_id: int,
        proctoring_id: int | None = None,
        violation_type: str | None = None,
    ) -> SnapshotItemSchema:
        """Обновляет информацию о снимке"""
        # Проверяем существование снимка
        snapshot = await self.snapshot_db_service.get_snapshot_by_id(
            snapshot_id=snapshot_id
        )
        
        if not snapshot:
            raise SnapshotNotFoundError()
        
        # Если указан новый proctoring_id, проверяем его существование
        if proctoring_id is not None and proctoring_id != snapshot.proctoring_id:
            proctoring = await self.proctoring_db_service.get_proctoring_by_id(
                proctoring_id=proctoring_id
            )
            if not proctoring:
                raise ProctoringNotFoundError
        
        updated_snapshot = await self.snapshot_db_service.update_snapshot(
            snapshot_id=snapshot_id,
            proctoring_id=proctoring_id,
            violation_type=violation_type
        )
        
        if not updated_snapshot:
            raise SnapshotNotFoundError()
        
        return SnapshotItemSchema.model_validate(updated_snapshot)
    
    @check_delete_rights
    async def delete_snapshot(self, *, snapshot_id: int) -> None:
        """Удаляет снимок"""
        snapshot = await self.snapshot_db_service.get_snapshot_by_id(
            snapshot_id=snapshot_id
        )
        
        if not snapshot:
            raise SnapshotNotFoundError()
        
        try:
            await s3_service.delete_snapshot(snapshot.object_key)
        except Exception as e:
            # Логируем ошибку, но продолжаем удаление из БД
            print(f"Warning: Failed to delete from S3: {str(e)}")
        
        await self.snapshot_db_service.delete_snapshot(snapshot_id=snapshot_id)
    
    @check_read_rights
    async def generate_pdf_report(self, *, proctoring_id: int) -> BinaryIO:
        """Генерирует PDF отчет по сессии прокторинга"""
        # Проверяем существование сессии
        if not await self.proctoring_db_service.get_proctoring_by_id(
            proctoring_id=proctoring_id
        ):
            raise ProctoringNotFoundError
        
        # Создаем сессию и генерируем отчет
        async with self.snapshot_db_service.get_async_session() as session:
            return await pdf_report_service.generate_report(
                proctoring_id=proctoring_id,
                session=session
            )
