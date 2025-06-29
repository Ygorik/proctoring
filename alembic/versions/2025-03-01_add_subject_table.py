"""Add_subject_table

Revision ID: 22756b6429d1
Revises: 44fb694d2876
Create Date: 2025-03-01 01:26:47.722106

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "22756b6429d1"
down_revision: Union[str, None] = "44fb694d2876"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "subject",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default="NOW()", nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default="NOW()", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "subject_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
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
    op.drop_table("subject_user")
    op.drop_table("subject")
    # ### end Alembic commands ###
