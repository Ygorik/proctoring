from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base_model import BaseDBMixin, BaseDB


class RoleDB(BaseDB, BaseDBMixin):
    __tablename__ = "role"

    name: Mapped[str]
    rights_create: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    rights_read: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    rights_update: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    rights_delete: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
