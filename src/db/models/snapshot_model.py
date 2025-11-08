from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import BaseDBMixin, BaseDB


class ProctoringSnapshotDB(BaseDB, BaseDBMixin):
    """Модель для хранения метаданных снимков нарушений при прокторинге"""
    __tablename__ = "proctoring_snapshot"

    proctoring_id: Mapped[int] = mapped_column(ForeignKey("proctoring.id", ondelete="CASCADE"))
    
    # S3/MinIO информация
    bucket_name: Mapped[str]  # Название bucket в хранилище
    object_key: Mapped[str]  # Ключ объекта: user_{id}/YYYY-MM-DD/HH-MM-SS-ms_type.jpg
    
    # Информация о нарушении
    violation_type: Mapped[str | None]  # absence_person, extra_person, looking_away, etc.
    
    # Связи
    proctoring: Mapped["ProctoringDB"] = relationship(
        foreign_keys=[proctoring_id],
        back_populates="snapshots"
    )
