"""add_proctoring_snapshot_table

Revision ID: 2025_10_25_add_snapshot
Revises: 0269e16731d6
Create Date: 2025-10-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2025_10_25_add_snapshot'
down_revision: Union[str, None] = '0269e16731d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу proctoring_snapshot
    op.create_table(
        'proctoring_snapshot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proctoring_id', sa.Integer(), nullable=False),
        sa.Column('bucket_name', sa.String(), nullable=False),
        sa.Column('object_key', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('violation_type', sa.String(), nullable=True),
        sa.Column('violation_severity', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_violation', sa.Boolean(), nullable=False, server_default='FALSE'),
        sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['proctoring_id'], ['proctoring.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем индексы для оптимизации запросов
    op.create_index('ix_proctoring_snapshot_proctoring_id', 'proctoring_snapshot', ['proctoring_id'])
    op.create_index('ix_proctoring_snapshot_timestamp', 'proctoring_snapshot', ['timestamp'])
    op.create_index('ix_proctoring_snapshot_is_violation', 'proctoring_snapshot', ['is_violation'])


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_proctoring_snapshot_is_violation', table_name='proctoring_snapshot')
    op.drop_index('ix_proctoring_snapshot_timestamp', table_name='proctoring_snapshot')
    op.drop_index('ix_proctoring_snapshot_proctoring_id', table_name='proctoring_snapshot')
    
    # Удаляем таблицу
    op.drop_table('proctoring_snapshot')
