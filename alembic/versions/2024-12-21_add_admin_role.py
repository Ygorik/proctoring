"""Add admin role

Revision ID: a837551f5b4e
Revises: f93c87c73e6c
Create Date: 2024-12-21 14:07:32.270939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a837551f5b4e"
down_revision: Union[str, None] = "f93c87c73e6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO role (id, name, rights_create, rights_read, rights_update, rights_delete) "
            "VALUES (1, 'admin', true, true, true, true);"
        )
    )


def downgrade() -> None:
    pass
