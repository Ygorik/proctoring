"""add_cascade_delete_for_subject_user

Revision ID: 784e108ab857
Revises: 2025_11_05_first_photo
Create Date: 2025-11-09 16:06:50.241444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '784e108ab857'
down_revision: Union[str, None] = '2025_11_05_first_photo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем старый foreign key constraint
    op.drop_constraint('subject_user_user_id_fkey', 'subject_user', type_='foreignkey')
    
    # Создаем новый foreign key constraint с CASCADE
    op.create_foreign_key(
        'subject_user_user_id_fkey', 
        'subject_user', 
        'user', 
        ['user_id'], 
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Удаляем foreign key с CASCADE
    op.drop_constraint('subject_user_user_id_fkey', 'subject_user', type_='foreignkey')
    
    # Восстанавливаем старый foreign key без CASCADE
    op.create_foreign_key(
        'subject_user_user_id_fkey', 
        'subject_user', 
        'user', 
        ['user_id'], 
        ['id']
    )
