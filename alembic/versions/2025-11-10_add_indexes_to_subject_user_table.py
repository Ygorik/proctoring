"""add_indexes_to_subject_user_table

Revision ID: a1b2c3d4e5f6
Revises: 3fdd65265588
Create Date: 2025-11-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '2025_11_09_cascade_deletes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем уникальный составной индекс на (subject_id, user_id)
    # Это предотвращает дублирование и ускоряет поиск по обоим полям
    op.create_index(
        'ix_subject_user_subject_id_user_id',
        'subject_user',
        ['subject_id', 'user_id'],
        unique=True
    )
    
    # Дополнительный индекс для поиска по user_id
    # (subject_id уже покрывается составным индексом)
    op.create_index(
        'ix_subject_user_user_id',
        'subject_user',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_subject_user_user_id', table_name='subject_user')
    op.drop_index('ix_subject_user_subject_id_user_id', table_name='subject_user')
