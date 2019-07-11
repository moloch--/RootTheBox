"""Cascade on Delete

Revision ID: 5ca019edf61f
Revises: 469f428604aa
Create Date: 2019-06-23 05:49:26.061932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ca019edf61f"
down_revision = "469f428604aa"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("penalty") as batch_op:
        batch_op.drop_constraint("penalty_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("penalty_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "penalty_ibfk_1", "penalty", "team", ["team_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "penalty_ibfk_2", "penalty", "flag", ["flag_id"], ["id"], ondelete="CASCADE"
    )

    with op.batch_alter_table("snapshot_team") as batch_op:
        batch_op.drop_constraint("snapshot_team_ibfk_1", type_="foreignkey")
    op.create_foreign_key(
        "snapshot_team_ibfk_1",
        "snapshot_team",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("snapshot_to_snapshot_team") as batch_op:
        batch_op.drop_constraint("snapshot_to_snapshot_team_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("snapshot_to_snapshot_team_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "snapshot_to_snapshot_team_ibfk_1",
        "snapshot_to_snapshot_team",
        "snapshot",
        ["snapshot_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "snapshot_to_snapshot_team_ibfk_2",
        "snapshot_to_snapshot_team",
        "snapshot_team",
        ["snapshot_team_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("snapshot_team_to_flag") as batch_op:
        batch_op.drop_constraint("snapshot_team_to_flag_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("snapshot_team_to_flag_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "snapshot_team_to_flag_ibfk_1",
        "snapshot_team_to_flag",
        "snapshot_team",
        ["snapshot_team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "snapshot_team_to_flag_ibfk_2",
        "snapshot_team_to_flag",
        "flag",
        ["flag_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("snapshot_team_to_game_level") as batch_op:
        batch_op.drop_constraint(
            "snapshot_team_to_game_level_ibfk_1", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "snapshot_team_to_game_level_ibfk_2", type_="foreignkey"
        )
    op.create_foreign_key(
        "snapshot_team_to_game_level_ibfk_1",
        "snapshot_team_to_game_level",
        "snapshot_team",
        ["snapshot_team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "snapshot_team_to_game_level_ibfk_2",
        "snapshot_team_to_game_level",
        "game_level",
        ["gam_level_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("team_to_box") as batch_op:
        batch_op.drop_constraint("team_to_box_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_box_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_box_ibfk_1",
        "team_to_box",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "team_to_box_ibfk_2",
        "team_to_box",
        "box",
        ["box_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("team_to_item") as batch_op:
        batch_op.drop_constraint("team_to_item_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_item_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_item_ibfk_1",
        "team_to_item",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "team_to_item_ibfk_2",
        "team_to_item",
        "market_item",
        ["item_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("team_to_source_code") as batch_op:
        batch_op.drop_constraint("team_to_source_code_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_source_code_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_source_code_ibfk_1",
        "team_to_source_code",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "team_to_source_code_ibfk_2",
        "team_to_source_code",
        "source_code",
        ["source_code_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("team_to_hint") as batch_op:
        batch_op.drop_constraint("team_to_hint_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_hint_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_hint_ibfk_1",
        "team_to_hint",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "team_to_hint_ibfk_2",
        "team_to_hint",
        "hint",
        ["hint_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("team_to_flag") as batch_op:
        batch_op.drop_constraint("team_to_flag_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_flag_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_flag_ibfk_1",
        "team_to_flag",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "team_to_flag_ibfk_2",
        "team_to_flag",
        "flag",
        ["flag_id"],
        ["id"],
        ondelete="CASCADE",
    )

    with op.batch_alter_table("team_to_game_level") as batch_op:
        batch_op.drop_constraint("team_to_game_level_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_game_level_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_game_level_ibfk_1",
        "team_to_game_level",
        "team",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "team_to_game_level_ibfk_2",
        "team_to_game_level",
        "game_level",
        ["game_level_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    with op.batch_alter_table("penalty") as batch_op:
        batch_op.drop_constraint("penalty_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("penalty_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "penalty_ibfk_1", "penalty", "team", ["team_id"], ["id"], ondelete="RESTRICT"
    )
    op.create_foreign_key(
        "penalty_ibfk_2", "penalty", "flag", ["flag_id"], ["id"], ondelete="RESTRICT"
    )

    with op.batch_alter_table("snapshot_team") as batch_op:
        batch_op.drop_constraint("snapshot_team_ibfk_1", type_="foreignkey")
    op.create_foreign_key(
        "snapshot_team_ibfk_1",
        "snapshot_team",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("snapshot_to_snapshot_team") as batch_op:
        batch_op.drop_constraint("snapshot_to_snapshot_team_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("snapshot_to_snapshot_team_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "snapshot_to_snapshot_team_ibfk_1",
        "snapshot_to_snapshot_team",
        "snapshot",
        ["snapshot_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "snapshot_to_snapshot_team_ibfk_2",
        "snapshot_to_snapshot_team",
        "snapshot_team",
        ["snapshot_team_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("snapshot_team_to_flag") as batch_op:
        batch_op.drop_constraint("snapshot_team_to_flag_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("snapshot_team_to_flag_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "snapshot_team_to_flag_ibfk_1",
        "snapshot_team_to_flag",
        "snapshot_team",
        ["snapshot_team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "snapshot_team_to_flag_ibfk_2",
        "snapshot_team_to_flag",
        "flag",
        ["flag_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("snapshot_team_to_game_level") as batch_op:
        batch_op.drop_constraint(
            "snapshot_team_to_game_level_ibfk_1", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "snapshot_team_to_game_level_ibfk_2", type_="foreignkey"
        )
    op.create_foreign_key(
        "snapshot_team_to_game_level_ibfk_1",
        "snapshot_team_to_game_level",
        "snapshot_team",
        ["snapshot_team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "snapshot_team_to_game_level_ibfk_2",
        "snapshot_team_to_game_level",
        "game_level",
        ["gam_level_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("team_to_box") as batch_op:
        batch_op.drop_constraint("team_to_box_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_box_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_box_ibfk_1",
        "team_to_box",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "team_to_box_ibfk_2",
        "team_to_box",
        "box",
        ["box_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("team_to_item") as batch_op:
        batch_op.drop_constraint("team_to_item_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_item_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_item_ibfk_1",
        "team_to_item",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "team_to_item_ibfk_2",
        "team_to_item",
        "market_item",
        ["item_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("team_to_source_code") as batch_op:
        batch_op.drop_constraint("team_to_source_code_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_source_code_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_source_code_ibfk_1",
        "team_to_source_code",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "team_to_source_code_ibfk_2",
        "team_to_source_code",
        "source_code",
        ["source_code_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("team_to_hint") as batch_op:
        batch_op.drop_constraint("team_to_hint_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_hint_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_hint_ibfk_1",
        "team_to_hint",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "team_to_hint_ibfk_2",
        "team_to_hint",
        "hint",
        ["hint_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("team_to_flag") as batch_op:
        batch_op.drop_constraint("team_to_flag_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_flag_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_flag_ibfk_1",
        "team_to_flag",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "team_to_flag_ibfk_2",
        "team_to_flag",
        "flag",
        ["flag_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    with op.batch_alter_table("team_to_game_level") as batch_op:
        batch_op.drop_constraint("team_to_game_level_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("team_to_game_level_ibfk_2", type_="foreignkey")
    op.create_foreign_key(
        "team_to_game_level_ibfk_1",
        "team_to_game_level",
        "team",
        ["team_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "team_to_game_level_ibfk_2",
        "team_to_game_level",
        "game_level",
        ["game_level_id"],
        ["id"],
        ondelete="RESTRICT",
    )
