"""Box Rewards

Revision ID: 18d11f218dfe
Revises: 5ca019edf61f
Create Date: 2019-06-24 11:48:06.497803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "18d11f218dfe"
down_revision = "5ca019edf61f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("box", sa.Column("_value", sa.INTEGER, nullable=True))


def downgrade():
    op.drop_column("box", "_value")
