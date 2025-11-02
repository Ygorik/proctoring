"""remove_uploaded_at_from_snapshot

Revision ID: 2025_11_01_remove_uploaded_at
Revises: 2025_10_25_add_snapshot
Create Date: 2025-11-01

Удаляет поле uploaded_at из proctoring_snapshot, так как оно дублирует
функционал created_at из BaseDBMixin
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_01_remove_uploaded_at'
down_revision: Union[str, None] = '2025_10_25_add_snapshot'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем колонку uploaded_at из таблицы proctoring_snapshot
    op.drop_column('proctoring_snapshot', 'uploaded_at')


def downgrade() -> None:
    # Восстанавливаем колонку uploaded_at
    op.add_column(
        'proctoring_snapshot',
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
