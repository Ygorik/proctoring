from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import BaseDBMixin, BaseDB


class ProctoringDB(BaseDB, BaseDBMixin):
    __tablename__ = "proctoring"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"))
    type_id: Mapped[int] = mapped_column(ForeignKey("proctoring_type.id"))
    result: Mapped[str] = mapped_column(nullable=True, default=None, server_default=None)

    user: Mapped["UserDB"] = relationship(back_populates="proctoring")
    subject_type: Mapped["SubjectDB"] = relationship(back_populates="proctoring")
    proctoring_type: Mapped["ProctoringTypeDB"] = relationship(
        back_populates="proctoring"
    )


class ProctoringTypeDB(BaseDB, BaseDBMixin):
    __tablename__ = "proctoring_type"

    name: Mapped[str]
    absence_person: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    extra_person: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    person_substitution: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    looking_away: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    mouth_opening: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    hints_outside: Mapped[bool] = mapped_column(default=False, server_default="FALSE")

    proctoring: Mapped["ProctoringDB"] = relationship(back_populates="proctoring_type")
