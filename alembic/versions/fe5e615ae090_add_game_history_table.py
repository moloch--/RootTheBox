"""add game history table

Revision ID: fe5e615ae090
Revises: de5d615ae090
Create Date: 2023-02-28 19:33:02.808038

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.expression import func

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

# revision identifiers, used by Alembic.
revision = "fe5e615ae090"
down_revision = "de5d615ae090"
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
    if not _has_table("game_history"):
        op.create_table(
            "game_history",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("created", sa.DateTime, nullable=True),
            sa.Column(
                "team_id",
                sa.Integer,
                sa.ForeignKey("team.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("_type", sa.VARCHAR(length=20), nullable=False),
            sa.Column("_value", sa.Integer, default=0, nullable=False),
        )


def downgrade():
    if _has_table("game_history"):
        op.drop_table("game_history")
