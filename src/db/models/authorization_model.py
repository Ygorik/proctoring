from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.db.models.base_model import BaseDBMixin, BaseDB


class AuthorizationDB(BaseDB, BaseDBMixin):
    __tablename__ = "authorization"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["UserDB"] = relationship(back_populates="authorization")
