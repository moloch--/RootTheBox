"""JuiceShop Updates

Revision ID: 71aa3c94b7f5
Revises: 18d11f218dfe
Create Date: 2019-11-14 08:52:52.530520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "71aa3c94b7f5"
down_revision = "18d11f218dfe"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "category",
        "_category",
        existing_type=sa.VARCHAR(length=24),
        type_=sa.VARCHAR(length=64),
    )


def downgrade():
    op.alter_column(
        "category",
        "_category",
        existing_type=sa.VARCHAR(length=64),
        type_=sa.VARCHAR(length=24),
    )
