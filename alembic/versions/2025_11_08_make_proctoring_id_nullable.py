"""Make proctoring_id nullable in proctoring_snapshot

Revision ID: 2025_11_08_001
Revises: 2025_11_05_add_first_photo
Create Date: 2025-11-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251108_nullable_pid'
down_revision: Union[str, None] = '2025_11_05_first_photo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Сделаем proctoring_id nullable в таблице proctoring_snapshot
    op.alter_column('proctoring_snapshot', 'proctoring_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade() -> None:
    # Откатываем обратно
    op.alter_column('proctoring_snapshot', 'proctoring_id',
               existing_type=sa.INTEGER(),
               nullable=False)
