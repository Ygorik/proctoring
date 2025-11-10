"""add_cascade_delete_for_user_relations_and_indexes

Revision ID: 2025_11_09_cascade_deletes
Revises: 2025_11_05_first_photo
Create Date: 2025-11-09 16:09:58.543554

Добавляет CASCADE удаление для связей user с таблицами proctoring и subject_user,
а также создает индексы для оптимизации запросов в таблице subject_user
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_09_cascade_deletes'
down_revision: Union[str, None] = '2025_11_04_tables_update'
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
    
    # Создаем индексы для оптимизации запросов в subject_user
    # Уникальный составной индекс предотвращает дублирование и ускоряет поиск
    op.create_index(
        'ix_subject_user_subject_id_user_id',
        'subject_user',
        ['subject_id', 'user_id'],
        unique=True
    )
    
    # Дополнительный индекс для поиска по user_id
    op.create_index(
        'ix_subject_user_user_id',
        'subject_user',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('ix_subject_user_user_id', table_name='subject_user')
    op.drop_index('ix_subject_user_subject_id_user_id', table_name='subject_user')
    
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
