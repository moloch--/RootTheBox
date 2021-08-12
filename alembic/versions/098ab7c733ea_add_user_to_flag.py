"""add user_to_flag

Revision ID: 098ab7c733ea
Revises: 4aa1bab989f8
Create Date: 2021-08-08 23:03:49.444306

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "098ab7c733ea"
down_revision = "4aa1bab989f8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_to_flag",
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "flag_id",
            sa.Integer,
            sa.ForeignKey("flag.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    op.add_column("category", sa.Column("_description", sa.VARCHAR(1024)))
    op.add_column("user", sa.Column("_expire", sa.DateTime))


def downgrade():
    op.drop_table("user_to_flag")
    op.drop_column("category", "_description")
    op.drop_column("user", "_expire")
