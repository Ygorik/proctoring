from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class BaseDB(DeclarativeBase): ...

class IdDBMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class DateDBMixin:
    created_at: Mapped[datetime] = mapped_column(server_default="NOW()")
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default="NOW()", onupdate=datetime.now()
    )


class BaseDBMixin(IdDBMixin, DateDBMixin):
    ...
