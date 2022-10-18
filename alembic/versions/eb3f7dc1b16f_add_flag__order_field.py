"""add flag _order field

Revision ID: eb3f7dc1b16f
Revises: 67bf6ca63a9c
Create Date: 2018-12-14 10:56:12.295780

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

# revision identifiers, used by Alembic.
revision = "eb3f7dc1b16f"
down_revision = "67bf6ca63a9c"
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
    if not _table_has_column("flag", "_order"):
        op.add_column("flag", sa.Column("_order", sa.INTEGER))
        op.create_index("order", "flag", ["_order"])


def downgrade():
    if _table_has_column("flag", "_order"):
        op.drop_column("flag", "_order")
