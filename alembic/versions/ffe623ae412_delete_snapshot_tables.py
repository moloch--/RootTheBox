"""delete snapshot table

Revision ID: ffe623ae412
Revises: fe5e615ae090
Create Date: 2023-03-11 19:33:02.808038

"""
import sqlalchemy as sa
from datetime import datetime
from alembic import op
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.sql.expression import func

conn = op.get_bind()
inspector = Inspector.from_engine(conn)
tables = inspector.get_table_names()

# revision identifiers, used by Alembic.
revision = "ffe623ae412"
down_revision = "fe5e615ae090"
branch_labels = None
depends_on = None

history = {}
flag_count = {}


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


def add_history(created, team_id, reason, value):
    conn = op.get_bind()
    conn.execute(
        f"INSERT INTO game_history (created, team_id, _type, _value) VALUES ('{created}', {team_id}, '{reason}', {value});"
    )


def check_flag(item):
    team_id = item[0]
    created = datetime.now()
    if str(team_id) in flag_count:
        flag_count[str(team_id)] += 1
    else:
        add_history(created, team_id, "flag_count", 0)
        flag_count[str(team_id)] = 1
    add_history(created, team_id, "flag_count", flag_count[str(team_id)])


def check_history(item):
    created = item[1]
    team_id = item[2]
    money = item[3]
    bots = item[4]
    if str(team_id) in history:
        team = history[str(team_id)]
        if bots != team["bots"]:
            history[str(team_id)]["bots"] = bots
            add_history(created, team_id, "bot_count", bots)
        elif money != team["money"]:
            history[str(team_id)]["money"] = money
            add_history(created, team_id, "score", money)
        return
    else:
        add_history(created, team_id, "bot_count", 0)
        add_history(created, team_id, "start", 0)
        if bots > 0:
            add_history(created, team_id, "bot_count", 0)
        if money > 0:
            add_history(created, team_id, "score", money)
        history[str(team_id)] = {"money": money, "bots": bots}


def upgrade():
    try:
        conn = op.get_bind()
        res = conn.execute("SELECT * FROM snapshot_team;")
        results = res.fetchall()
        i = 0
        for item in results:
            check_history(item)
            i += 1
        if i > 0:
            conn.execute("COMMIT;")

    except Exception as e:
        print("Failed to import prior snapshot data into game history: %s" % str(e))
        print("Continuing...")
    try:
        res = conn.execute("SELECT * FROM team_to_flag;")
        results = res.fetchall()
        i = 0
        for item in results:
            check_flag(item)
            i += 1
        if i > 0:
            conn.execute("COMMIT;")
    except Exception as e:
        print("Failed to import prior flag count into game history: %s" % str(e))
        print("Continuing...")

    if _has_table("snapshot_to_snapshot_team"):
        op.drop_table("snapshot_to_snapshot_team")
    if _has_table("snapshot_team_to_game_level"):
        op.drop_table("snapshot_team_to_game_level")
    if _has_table("snapshot_team_to_flag"):
        op.drop_table("snapshot_team_to_flag")
    if _has_table("snapshot_team"):
        op.drop_table("snapshot_team")
    if _has_table("snapshot"):
        op.drop_table("snapshot")


def downgrade():
    print("No downgrade for this")
    pass
