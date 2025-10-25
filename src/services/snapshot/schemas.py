"""Схемы для работы со снимками прокторинга"""
from datetime import datetime
from pydantic import Field

from src.base_schemas import BaseResponseSchemas


class SnapshotCreateSchema(BaseResponseSchemas):
    """Схема для создания нового снимка"""
    proctoring_id: int = Field(..., description="ID сессии прокторинга")
    violation_type: str | None = Field(None, description="Тип нарушения")
    violation_severity: str | None = Field(None, description="Серьезность нарушения: low, medium, high")
    description: str | None = Field(None, description="Описание нарушения")
    is_violation: bool = Field(False, description="Флаг наличия нарушения")
    metadata_json: dict | None = Field(None, description="Дополнительные метаданные")


class SnapshotItemSchema(BaseResponseSchemas):
    """Схема для отображения снимка"""
    id: int
    proctoring_id: int
    object_key: str
    file_size: int
    content_type: str
    timestamp: datetime
    violation_type: str | None
    violation_severity: str | None
    description: str | None
    is_violation: bool
    created_at: datetime


class SnapshotListSchema(BaseResponseSchemas):
    """Схема для списка снимков"""
    snapshots: list[SnapshotItemSchema]
    total_count: int
    violations_count: int


class SnapshotFilters(BaseResponseSchemas):
    """Фильтры для поиска снимков"""
    proctoring_id: int | None = None
    user_id: int | None = None
    is_violation: bool | None = None
    violation_type: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
