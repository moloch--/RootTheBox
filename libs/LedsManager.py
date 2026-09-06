#!/usr/bin/env python3
import logging
from datetime import datetime
from requests import post
from requests.exceptions import RequestException
from tornado.options import options

TIMEOUT = 2

# Last led api failure, so the admin interface can report it in a red banner
LAST_ERROR = None

def get_last_error():
    """Returns the last led api error message, None when the api is healthy"""
    return LAST_ERROR

def clear_last_error():
    global LAST_ERROR
    LAST_ERROR = None

def _fail(message):
    """Logs an error and keeps it around for the admin interface"""
    global LAST_ERROR
    logging.error(message)
    LAST_ERROR = "%s - %s" % (datetime.now().strftime("%H:%M:%S"), message)
    return LAST_ERROR

def _post(endpoint, payload):
    """Posts to the led api, returns an error message or None on success"""
    url = options.led_base_api + endpoint
    try:
        rq = post(url, json=payload, timeout=TIMEOUT)
    except RequestException as error:
        return _fail(f"{url} not reachable !!! payload: {payload} | error: {error}")
    if rq.status_code != 200:
        return _fail(f"{url} returned an error !!! payload: {payload} | status_code: {rq.status_code}")
    clear_last_error()
    return None

def get_teams():
    """Returns the teams from the database, ordered by creation (id)"""
    from models.Team import Team
    from models import dbsession

    return dbsession.query(Team).order_by(Team.id).all()

def _table_for(team_name):
    """Returns a (table_id, error message) couple for the given team"""
    from models.Team import Team

    team = Team.by_name(team_name)
    if team is None:
        return None, _fail(f"Team `{team_name}` not found in database")
    if team.table_id is None:
        return None, _fail(f"No table assigned to team `{team_name}`, see /admin/leds")
    return team.table_id, None

def get_table_id_by_team_name(team_name):
    """Returns the table assigned to the team, or None when unassigned"""
    table_id, _ = _table_for(team_name)
    return table_id

def led_flag(team_name):
    table_id, error = _table_for(team_name)
    if error is not None:
        return error
    return _post("flag", {"table": table_id, "color": options.led_color_flag})


def led_own(team_name):
    table_id, error = _table_for(team_name)
    if error is not None:
        return error
    return _post("box", {"table": table_id, "color": options.led_color_box})

ROUND = 1
def led_round_start():
    global ROUND
    payload = {
        "duration": options.led_round_duration,
        "round": "finale" if ROUND == 4 else ROUND,
        "color": options.led_color_round,
    }
    error = _post("round", payload)
    ROUND+=1
    return error

def led_stop():
    return _post("forceColor", {"duration": options.led_stop_duration, "color": options.led_color_stop})

def led_test(table_id):
    """Lights up a single table, used by the admin leds page"""
    return _post("flag", {"table": int(table_id), "color": options.led_color_flag})

if __name__ == '__main__':
    import sys

    teams = get_teams()
    team_name = sys.argv[1] if len(sys.argv) > 1 else teams[0].name
    led_flag(team_name)  # Should not log errors

    # Test own function
    led_own(team_name)  # Should not log errors

    # Test round_start function
    led_round_start()  # Should not log errors
