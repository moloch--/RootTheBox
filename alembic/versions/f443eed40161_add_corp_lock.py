"""add corp lock

Revision ID: f443eed40161
Revises: ffe623ae412
Create Date: 2023-05-27 17:01:22.454528

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.expression import func

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

# revision identifiers, used by Alembic.
revision = "f443eed40161"
down_revision = "ffe623ae412"
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
    if not _table_has_column("corporation", "_locked"):
        op.add_column("corporation", sa.Column("_locked", sa.BOOLEAN))
    if not _table_has_column("game_level", "_locked"):
        op.add_column("game_level", sa.Column("_locked", sa.BOOLEAN))


def downgrade():
    if _table_has_column("corporation", "_locked"):
        op.drop_column("corporation", "_locked")
    if _table_has_column("game_level", "_locked"):
        op.drop_column("game_level", "_locked")
