"""Схемы для работы со снимками прокторинга"""
from datetime import datetime
from pydantic import Field

from src.base_schemas import BaseResponseSchemas


class SnapshotCreateSchema(BaseResponseSchemas):
    """Схема для создания нового снимка"""
    proctoring_id: int = Field(..., description="ID сессии прокторинга")
    violation_type: str | None = Field(None, description="Тип нарушения")


class SnapshotItemSchema(BaseResponseSchemas):
    """Схема для отображения снимка"""
    id: int
    proctoring_id: int
    bucket_name: str
    object_key: str
    violation_type: str | None
    created_at: datetime


class SnapshotListSchema(BaseResponseSchemas):
    """Схема для списка снимков"""
    snapshots: list[SnapshotItemSchema]
    total_count: int


class SnapshotFilters(BaseResponseSchemas):
    """Фильтры для поиска снимков"""
    proctoring_id: int | None = None
    violation_type: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
