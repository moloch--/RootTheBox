"""add email field

Revision ID: 67bf6ca63a9c
Revises: 9783dbd4d5fe
Create Date: 2018-12-09 22:51:59.947266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "67bf6ca63a9c"
down_revision = "9783dbd4d5fe"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("_email", sa.VARCHAR(length=64)))


def downgrade():
    op.drop_column("user", "_email")
