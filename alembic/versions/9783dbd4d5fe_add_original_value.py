"""add original_value

Revision ID: 9783dbd4d5fe
Revises: 
Create Date: 2018-12-09 16:53:45.599267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9783dbd4d5fe"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "hint",
        "_description",
        existing_type=sa.VARCHAR(length=512),
        type_=sa.VARCHAR(length=1024),
    )
    op.add_column("flag", sa.Column("_original_value", sa.INTEGER))


def downgrade():
    op.alter_column(
        "hint",
        "_description",
        existing_type=sa.VARCHAR(length=1024),
        type_=sa.VARCHAR(length=512),
    )
    op.drop_column("flag", "_original_value")
