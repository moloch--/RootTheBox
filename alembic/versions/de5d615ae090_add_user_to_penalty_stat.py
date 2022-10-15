"""add user to penalty stat

Revision ID: de5d615ae090
Revises: 31918b83c372
Create Date: 2022-10-14 19:33:02.808038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "de5d615ae090"
down_revision = "31918b83c372"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("penalty", sa.Column("user_id", sa.INTEGER))
    op.create_foreign_key(
        "penalty_ibfk_3",
        "penalty",
        "user",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_column("penalty", "user_id")
