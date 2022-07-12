"""add password_token table

Revision ID: 8fa7d8ac2b2f
Revises: 9443ded40161
Create Date: 2020-09-06 19:23:34.831352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8fa7d8ac2b2f"
down_revision = "9443ded40161"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_token",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created", sa.DateTime, nullable=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.VARCHAR(length=64), nullable=False, unique=True),
        sa.Column("used", sa.BOOLEAN),
    )


def downgrade():
    op.drop_table("password_token")
