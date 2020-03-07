"""add descriptive columns

Revision ID: bc091b7be912
Revises: bd7bd19e98bd
Create Date: 2020-03-03 18:23:40.855666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bc091b7be912"
down_revision = "bd7bd19e98bd"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("_notes", sa.VARCHAR(512)))
    op.add_column("team", sa.Column("_notes", sa.VARCHAR(512)))
    op.add_column("game_level", sa.Column("_description", sa.VARCHAR(512)))
    op.add_column("corporation", sa.Column("_description", sa.VARCHAR(512)))


def downgrade():
    op.drop_column("user", "_notes")
    op.drop_column("team", "_notes")
    op.drop_column("game_level", "_description")
    op.drop_column("corporation", "_description")
