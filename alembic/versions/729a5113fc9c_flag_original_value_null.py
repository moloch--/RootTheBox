"""flag original_value null

Revision ID: 729a5113fc9c
Revises: eb3f7dc1b16f
Create Date: 2019-02-26 21:13:42.243218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "729a5113fc9c"
down_revision = "eb3f7dc1b16f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("flag") as batch_op:
        batch_op.alter_column(
            "_original_value", existing_type=sa.INTEGER, nullable=True
        )


def downgrade():
    with op.batch_alter_table("flag") as batch_op:
        batch_op.alter_column(
            "_original_value", existing_type=sa.INTEGER, nullable=False
        )
