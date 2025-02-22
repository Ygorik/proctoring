from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.db.models.base_model import BaseDBMixin, BaseDB


class UserDB(BaseDB, BaseDBMixin):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default="uuid_generate_v4()"
    )

    login: Mapped[str]
    hashed_password: Mapped[str]
    full_name: Mapped[str]

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))

    authorization: Mapped["AuthorizationDB"] = relationship(back_populates="user")
    role: Mapped["RoleDB"] = relationship(back_populates="user")
