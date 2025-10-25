from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import BaseDBMixin, BaseDB


class ProctoringSnapshotDB(BaseDB, BaseDBMixin):
    """Модель для хранения метаданных фотографий из MinIO"""
    __tablename__ = "proctoring_snapshot"

    proctoring_id: Mapped[int] = mapped_column(ForeignKey("proctoring.id", ondelete="CASCADE"))
    
    # MinIO информация
    bucket_name: Mapped[str]  # Название bucket в MinIO
    object_key: Mapped[str]  # Ключ объекта: user_{id}/YYYY-MM-DD/timestamp_type.jpg
    file_size: Mapped[int]  # Размер файла в байтах
    content_type: Mapped[str]  # MIME-type (image/jpeg, image/png)
    
    # Временные метки
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # Когда сделан снимок
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # Когда загружен в MinIO
    
    # Информация о нарушении
    violation_type: Mapped[str | None]  # absence_person, extra_person, looking_away, etc.
    violation_severity: Mapped[str | None]  # low, medium, high
    description: Mapped[str | None]  # Дополнительное описание
    is_violation: Mapped[bool] = mapped_column(default=False)  # Флаг наличия нарушения
    
    # Дополнительные метаданные в JSON
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Связи
    proctoring: Mapped["ProctoringDB"] = relationship(back_populates="snapshots")
