"""rename column visible

Revision ID: cd4d09aa9c68
Revises: 098ab7c733ea
Create Date: 2022-01-05 10:00:05.629776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cd4d09aa9c68"
down_revision = "098ab7c733ea"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("ip_address") as batch_op:
        batch_op.alter_column(
            "visable", new_column_name="visible", existing_type=sa.BOOLEAN
        )


def downgrade():
    with op.batch_alter_table("ip_address") as batch_op:
        batch_op.alter_column(
            "visible", new_column_name="visable", existing_type=sa.BOOLEAN
        )
