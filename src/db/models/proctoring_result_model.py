from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_model import BaseDBMixin, BaseDB


class ProctoringResultDB(BaseDB, BaseDBMixin):
    __tablename__ = "proctoring_result"

    detected_absence_person: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    detected_extra_person: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    detected_person_substitution: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    detected_looking_away: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    detected_mouth_opening: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    detected_hints_outside: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )

    proctoring: Mapped["ProctoringDB"] = relationship(
        back_populates="proctoring_result"
    )
