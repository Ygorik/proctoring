"""Add superuser

Revision ID: 44fb694d2876
Revises: a837551f5b4e
Create Date: 2024-12-21 09:40:52.438211

"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.utils.cryptographer import Cryptographer

# revision identifiers, used by Alembic.
revision: str = '44fb694d2876'
down_revision: Union[str, None] = 'a837551f5b4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    hashed_password = Cryptographer(os.getenv("CRYPTO_KEY")).encrypt("password")  # Change password

    op.execute(
        sa.text(
            "INSERT INTO \"user\" (login, hashed_password, full_name, role_id) "
            f"VALUES ('admin', '{hashed_password}', 'Администартор', 1);"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM \"user\" WHERE login='admin';"
        )
    )
