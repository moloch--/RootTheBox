"""add_team_table_id

Revision ID: b3f1c0d7ae21
Revises: 1ee5b63e716f
Create Date: 2026-09-05 00:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b3f1c0d7ae21'
down_revision = '1ee5b63e716f'
branch_labels = None
depends_on = None

try:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
except:
    conn = None
    inspector = None
    tables = None

def _table_has_column(table, column):
    if not inspector:
        return True
    has_column = False
    for col in inspector.get_columns(table):
        if column not in col["name"]:
            continue
        has_column = True
    return has_column


def upgrade():
    if not _table_has_column("team", "_table_id"):
        op.add_column("team", sa.Column("_table_id", sa.Integer()))


def downgrade():
    if _table_has_column("team", "_table_id"):
        op.drop_column("team", "_table_id")
