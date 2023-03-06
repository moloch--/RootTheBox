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
    with op.batch_alter_table("category") as batch_op:
        batch_op.alter_column(
            "_category",
            existing_type=sa.VARCHAR(length=24),
            type_=sa.VARCHAR(length=64),
        )


def downgrade():
    with op.batch_alter_table("category") as batch_op:
        batch_op.alter_column(
            "_category",
            existing_type=sa.VARCHAR(length=64),
            type_=sa.VARCHAR(length=24),
        )
