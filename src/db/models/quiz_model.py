from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import BaseDBMixin, BaseDB


class QuizDB(BaseDB, BaseDBMixin):
    __tablename__ = "quiz"

    name: Mapped[str]

    proctoring: Mapped["ProctoringDB"] = relationship(back_populates="quiz")
