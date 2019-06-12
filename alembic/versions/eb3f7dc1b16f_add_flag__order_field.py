"""add flag _order field

Revision ID: eb3f7dc1b16f
Revises: 67bf6ca63a9c
Create Date: 2018-12-14 10:56:12.295780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb3f7dc1b16f"
down_revision = "67bf6ca63a9c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("flag", sa.Column("_order", sa.INTEGER))
    op.create_index("order", "flag", ["_order"])


def downgrade():
    op.drop_column("flag", "_order")
