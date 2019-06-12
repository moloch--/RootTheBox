"""box _capture_message

Revision ID: 469f428604aa
Revises: 729a5113fc9c
Create Date: 2019-04-06 21:11:56.017968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "469f428604aa"
down_revision = "729a5113fc9c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("box", sa.Column("_capture_message", sa.VARCHAR(length=1024)))


def downgrade():
    op.drop_column("box", "_capture_message")
