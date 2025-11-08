"""add_first_photo_to_proctoring

Revision ID: 2025_11_05_first_photo
Revises: 2025_11_04_tables_update
Create Date: 2025-11-05

Добавляет поле first_photo_id в таблицу proctoring для хранения ссылки на фото студента
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_05_first_photo'
down_revision: Union[str, None] = '2025_11_04_tables_update'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле first_photo_id с внешним ключом на proctoring_snapshot
    op.add_column('proctoring', 
        sa.Column('first_photo_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_proctoring_first_photo',
        'proctoring', 'proctoring_snapshot',
        ['first_photo_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Удаляем внешний ключ и колонку
    op.drop_constraint('fk_proctoring_first_photo', 'proctoring', type_='foreignkey')
    op.drop_column('proctoring', 'first_photo_id')
