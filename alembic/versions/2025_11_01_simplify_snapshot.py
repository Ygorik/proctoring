"""simplify_snapshot_table

Revision ID: 2025_11_01_simplify_snapshot
Revises: 2025_11_01_remove_uploaded_at
Create Date: 2025-11-01

Упрощает таблицу proctoring_snapshot, удаляя избыточные поля:
- file_size, content_type (дублируются в metadata_json)
- timestamp (используется created_at из BaseDBMixin)
- violation_severity (не используется, определяется внешней логикой)
- description (избыточно при наличии violation_type)
- is_violation (избыточно - если есть violation_type, значит есть нарушение)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2025_11_01_simplify_snapshot'
down_revision: Union[str, None] = '2025_11_01_remove_uploaded_at'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем избыточные колонки
    op.drop_column('proctoring_snapshot', 'file_size')
    op.drop_column('proctoring_snapshot', 'content_type')
    op.drop_column('proctoring_snapshot', 'timestamp')
    op.drop_column('proctoring_snapshot', 'violation_severity')
    op.drop_column('proctoring_snapshot', 'description')
    op.drop_column('proctoring_snapshot', 'is_violation')


def downgrade() -> None:
    # Восстанавливаем колонки
    op.add_column('proctoring_snapshot', sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('proctoring_snapshot', sa.Column('content_type', sa.String(), nullable=False, server_default='image/jpeg'))
    op.add_column('proctoring_snapshot', sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')))
    op.add_column('proctoring_snapshot', sa.Column('violation_severity', sa.String(), nullable=True))
    op.add_column('proctoring_snapshot', sa.Column('description', sa.String(), nullable=True))
    op.add_column('proctoring_snapshot', sa.Column('is_violation', sa.Boolean(), nullable=False, server_default='FALSE'))
