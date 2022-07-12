"""add flag lock

Revision ID: 83f862086ff0
Revises: cd4d09aa9c68
Create Date: 2022-05-13 21:46:22.838283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "83f862086ff0"
down_revision = "cd4d09aa9c68"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("flag", sa.Column("_locked", sa.BOOLEAN))


def downgrade():
    op.drop_column("flag", "_locked")
