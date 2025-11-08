"""simplify_snapshot

Revision ID: 2025_11_01_simplify_snapshot
Revises: 2025_10_25_add_snapshot
Create Date: 2025-11-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2025_11_01_simplify_snapshot'
down_revision: Union[str, None] = '2025_10_25_add_snapshot'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Упрощение структуры snapshot - добавьте нужные изменения здесь
    pass


def downgrade() -> None:
    # Откат изменений
    pass
