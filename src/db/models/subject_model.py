from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import BaseDBMixin, BaseDB


class SubjectDB(BaseDB, BaseDBMixin):
    __tablename__ = "subject"

    name: Mapped[str]

    proctoring: Mapped["ProctoringDB"] = relationship(back_populates="subject")


class SubjectUserDB(BaseDB):
    __tablename__ = "subject_user"
    __table_args__ = (
        Index('ix_subject_user_subject_id_user_id', 'subject_id', 'user_id', unique=True),
        Index('ix_subject_user_user_id', 'user_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
