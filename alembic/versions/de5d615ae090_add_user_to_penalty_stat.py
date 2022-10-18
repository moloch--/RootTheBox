"""add user to penalty stat

Revision ID: de5d615ae090
Revises: 31918b83c372
Create Date: 2022-10-14 19:33:02.808038

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

# revision identifiers, used by Alembic.
revision = "de5d615ae090"
down_revision = "31918b83c372"
branch_labels = None
depends_on = None


def _table_has_column(table, column):
    has_column = False
    for col in inspector.get_columns(table):
        if column not in col["name"]:
            continue
        has_column = True
    return has_column


def _has_table(table_name):
    tables = inspector.get_table_names()
    return table_name in tables


def upgrade():
    if not _table_has_column("penalty", "user_id"):
        with op.batch_alter_table("penalty") as batch_op:
            batch_op.add_column(sa.Column("user_id", sa.INTEGER))
            batch_op.create_foreign_key(
                "penalty_ibfk_3",
                "user",
                ["user_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade():
    if _table_has_column("penalty", "user_id"):
        op.drop_column("penalty", "user_id")
