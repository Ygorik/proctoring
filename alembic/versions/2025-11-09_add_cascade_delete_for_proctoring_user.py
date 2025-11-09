"""add_cascade_delete_for_proctoring_user

Revision ID: 3fdd65265588
Revises: 784e108ab857
Create Date: 2025-11-09 16:09:58.543554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fdd65265588'
down_revision: Union[str, None] = '784e108ab857'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем старый foreign key constraint
    op.drop_constraint('proctoring_user_id_fkey', 'proctoring', type_='foreignkey')
    
    # Создаем новый foreign key constraint с CASCADE
    op.create_foreign_key(
        'proctoring_user_id_fkey', 
        'proctoring', 
        'user', 
        ['user_id'], 
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Удаляем foreign key с CASCADE
    op.drop_constraint('proctoring_user_id_fkey', 'proctoring', type_='foreignkey')
    
    # Восстанавливаем старый foreign key без CASCADE
    op.create_foreign_key(
        'proctoring_user_id_fkey', 
        'proctoring', 
        'user', 
        ['user_id'], 
        ['id']
    )
