"""add_cascade_delete_for_user_relations

Revision ID: 2025_11_09_cascade_deletes
Revises: 2025_11_05_first_photo
Create Date: 2025-11-09 16:09:58.543554

Добавляет CASCADE удаление для связей user с таблицами proctoring и subject_user
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_09_cascade_deletes'
down_revision: Union[str, None] = '2025_11_05_first_photo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем CASCADE для subject_user.user_id
    op.drop_constraint('subject_user_user_id_fkey', 'subject_user', type_='foreignkey')
    op.create_foreign_key(
        'subject_user_user_id_fkey', 
        'subject_user', 
        'user', 
        ['user_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Добавляем CASCADE для proctoring.user_id
    op.drop_constraint('proctoring_user_id_fkey', 'proctoring', type_='foreignkey')
    op.create_foreign_key(
        'proctoring_user_id_fkey', 
        'proctoring', 
        'user', 
        ['user_id'], 
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Откатываем CASCADE для proctoring.user_id
    op.drop_constraint('proctoring_user_id_fkey', 'proctoring', type_='foreignkey')
    op.create_foreign_key(
        'proctoring_user_id_fkey', 
        'proctoring', 
        'user', 
        ['user_id'], 
        ['id']
    )
    
    # Откатываем CASCADE для subject_user.user_id
    op.drop_constraint('subject_user_user_id_fkey', 'subject_user', type_='foreignkey')
    op.create_foreign_key(
        'subject_user_user_id_fkey', 
        'subject_user', 
        'user', 
        ['user_id'], 
        ['id']
    )
