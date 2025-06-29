"""Add user models

Revision ID: f93c87c73e6c
Revises: 
Create Date: 2024-12-21 13:22:10.734958

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f93c87c73e6c"
down_revision: Union[str, None] = "896f305c75a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "rights_create", sa.Boolean(), server_default="FALSE", nullable=False
        ),
        sa.Column("rights_read", sa.Boolean(), server_default="FALSE", nullable=False),
        sa.Column(
            "rights_update", sa.Boolean(), server_default="FALSE", nullable=False
        ),
        sa.Column(
            "rights_delete", sa.Boolean(), server_default="FALSE", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default="NOW()",
            default="NOW()",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default="NOW()",
            default="NOW()",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default="NOW()",
            default="NOW()",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default="NOW()",
            default="NOW()",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "authorization",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default="NOW()",
            default="NOW()",
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default="NOW()",
            default="NOW()",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("authorization")
    op.drop_table("user")
    op.drop_table("role")
    # ### end Alembic commands ###
