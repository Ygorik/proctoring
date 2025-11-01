from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.db.models.base_model import BaseDBMixin, BaseDB


class UserDB(BaseDB, BaseDBMixin):
    __tablename__ = "user"

    login: Mapped[str | None] = mapped_column(server_default="NULL", default=None)
    hashed_password: Mapped[str | None] = mapped_column(server_default="NULL", default=None)
    full_name: Mapped[str]

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))

    authorization: Mapped["AuthorizationDB"] = relationship(back_populates="user")
    role: Mapped["RoleDB"] = relationship(back_populates="user")
    proctoring: Mapped["ProctoringDB"] = relationship(back_populates="user")
