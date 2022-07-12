"""add email token

Revision ID: 4aa1bab989f8
Revises: 324e65d824d1
Create Date: 2021-01-29 13:39:42.842889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4aa1bab989f8"
down_revision = "324e65d824d1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "email_token",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created", sa.DateTime, nullable=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.VARCHAR(length=64), nullable=False, unique=True),
        sa.Column("valid", sa.BOOLEAN),
    )


def downgrade():
    op.drop_table("email_token")
