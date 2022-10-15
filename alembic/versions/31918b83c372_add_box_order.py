"""add box order

Revision ID: 31918b83c372
Revises: 83f862086ff0
Create Date: 2022-10-12 23:02:22.212759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "31918b83c372"
down_revision = "83f862086ff0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("box", sa.Column("_order", sa.INTEGER))
    op.create_index("order", "box", ["_order"])


def downgrade():
    op.drop_column("box", "_order")
