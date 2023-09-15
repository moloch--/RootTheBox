"""expand_field_size

Revision ID: a143abd40133
Revises: f443eed40161
Create Date: 2023-08-14 17:01:22.454528

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.expression import func

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

# revision identifiers, used by Alembic.
revision = "a143abd40133"
down_revision = "f443eed40161"
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
    with op.batch_alter_table("hint") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=1024),
            type_=sa.VARCHAR(length=4096),
        )
    with op.batch_alter_table("box") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=1024),
            type_=sa.VARCHAR(length=4096),
        )
        batch_op.alter_column(
            "_capture_message",
            existing_type=sa.VARCHAR(length=1024),
            type_=sa.VARCHAR(length=4096),
        )
    with op.batch_alter_table("flag") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=1024),
            type_=sa.VARCHAR(length=4096),
        )
        batch_op.alter_column(
            "_capture_message",
            existing_type=sa.VARCHAR(length=512),
            type_=sa.VARCHAR(length=4096),
        )
    with op.batch_alter_table("category") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=1024),
            type_=sa.VARCHAR(length=4096),
        )
    with op.batch_alter_table("source_code") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=1024),
            type_=sa.VARCHAR(length=4096),
        )


def downgrade():
    with op.batch_alter_table("hint") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=1024),
        )
    with op.batch_alter_table("box") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=1024),
        )
        batch_op.alter_column(
            "_capture_message",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=1024),
        )
    with op.batch_alter_table("flag") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=1024),
        )
        batch_op.alter_column(
            "_capture_message",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=512),
        )
    with op.batch_alter_table("category") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=1024),
        )
    with op.batch_alter_table("source_code") as batch_op:
        batch_op.alter_column(
            "_description",
            existing_type=sa.VARCHAR(length=4096),
            type_=sa.VARCHAR(length=1024),
        )
