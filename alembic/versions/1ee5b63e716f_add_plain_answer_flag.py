"""add_plain_answer_flag

Revision ID: 1ee5b63e716f
Revises: a143abd40133
Create Date: 2024-02-15 11:17:27.270274

"""
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.expression import func

from alembic import op

# revision identifiers, used by Alembic.
revision = '1ee5b63e716f'
down_revision = 'a143abd40133'
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


def _has_table(table_name):
    tables = inspector.get_table_names()
    return table_name in tables


def upgrade():
    if not _table_has_column("flag", "_plain_answer"):
        op.add_column("flag", sa.Column("_plain_answer", sa.VARCHAR(256)))


def downgrade():
    if _table_has_column("flag", "_plain_answer"):
        op.drop_column("flag", "_plain_answer")
