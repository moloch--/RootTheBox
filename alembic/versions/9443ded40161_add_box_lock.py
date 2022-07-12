"""add box lock

Revision ID: 9443ded40161
Revises: bc091b7be912
Create Date: 2020-03-07 17:01:22.454528

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9443ded40161"
down_revision = "bc091b7be912"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("box", sa.Column("_locked", sa.BOOLEAN))


def downgrade():
    op.drop_column("box", "_locked")
