"""sourcecode cascade

Revision ID: bd7bd19e98bd
Revises: 71aa3c94b7f5
Create Date: 2020-02-22 10:37:39.239191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bd7bd19e98bd"
down_revision = "71aa3c94b7f5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("source_code") as batch_op:
        batch_op.drop_constraint("source_code_ibfk_1", type_="foreignkey")
    op.create_foreign_key(
        "source_code_ibfk_1",
        "source_code",
        "box",
        ["box_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    with op.batch_alter_table("source_code") as batch_op:
        batch_op.drop_constraint("source_code_ibfk_1", type_="foreignkey")
    op.create_foreign_key(
        "source_code_ibfk_1",
        "source_code",
        "box",
        ["box_id"],
        ["id"],
        ondelete="RESTRICT",
    )
