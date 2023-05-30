# -*- coding: utf-8 -*-

"""
Created on Oct 04, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
# pylint: disable=no-member


import json
import logging
import time

from threading import Thread
from sqlalchemy.orm import scoped_session
from models import dbsession, session_maker
from models.Team import Team
from models.Box import Box
from models.User import User
from models.Flag import Flag
from models.Hint import Hint
from models.GameLevel import GameLevel
from libs.BotManager import BotManager
from libs.EventManager import EventManager
from tornado.options import options
from builtins import object, str
from collections import OrderedDict


class Scoreboard(object):
    """Manages websocket connections (mostly thread safe)"""

    @classmethod
    def now(cls, app):
        """Returns the current game state"""
        return json.dumps(app.settings["scoreboard_state"].get("teams"))

    @classmethod
    def update_gamestate(cls, app):
        game_levels = GameLevel.all()
        teams = Team.ranks()
        users = User.ranks()
        bots = BotManager.instance().count_all_teams()
        game_state = {
            "teams": OrderedDict(),
            "users": OrderedDict(),
            "levels": {},
            "boxes": {},
            "hint_count": len(Hint.all()),
            "flag_count": len(Flag.all()),
            "box_count": len(Box.unlocked()),
            "level_count": len(game_levels),
        }
        for team in teams:
            millis = int(round(time.time() * 1000))
            game_state["teams"][team.name] = {
                "uuid": team.uuid,
                "flags": [flag.uuid for flag in team.flags],
                "game_levels": [str(lvl) for lvl in team.game_levels],
                "members_count": len(team.members),
                "hints_count": len(team.hints),
                "bot_count": bots[team.uuid],
                "money": team.money,
                "users": [user.uuid for user in team.members],
            }

            highlights = {"money": 0, "flag": 0, "bot": 0, "hint": 0}
            for item in highlights:
                value = team.get_score(item)
                game_state["teams"][team.name][item] = value
                scoreboard_history = app.settings["scoreboard_history"]
                if team.name in scoreboard_history:
                    prev = scoreboard_history[team.name][item]
                    if prev < value:
                        highlights[item] = millis
                    else:
                        highlights[item] = scoreboard_history[team.name]["highlights"][
                            item
                        ]
            highlights["now"] = millis
            game_state["teams"][team.name]["highlights"] = highlights
            app.settings["scoreboard_history"][team.name] = game_state["teams"].get(
                team.name
            )
        for idx, user in enumerate(users):
            if idx < options.mvp_max:
                game_state["users"][user.handle] = {"money": user.money}
            else:
                break
        for level in game_levels:
            game_state["levels"][level.name] = {
                "type": level.type,
                "number": level.number,
                "teams": {},
                "boxes": {},
                "box_count": len(level.unlocked_boxes()),
                "flag_count": len(level.flags),
            }
            for team in teams:
                game_state["levels"][level.name]["teams"][team.name] = {
                    "lvl_count": len(team.level_flags(level.number)),
                    "lvl_unlock": level in team.game_levels,
                }
            for box in sorted(level.unlocked_boxes()):
                game_state["levels"][level.name]["boxes"][box.uuid] = {
                    "name": box.name,
                    "locked": box.locked,
                    "teams": {},
                    "flags": {},
                    "flag_count": len(box.flags),
                }
                for team in teams:
                    game_state["levels"][level.name]["boxes"][box.uuid]["teams"][
                        team.name
                    ] = {"box_count": len(team.box_flags(box))}
                for flag in sorted(box.flags):
                    game_state["levels"][level.name]["boxes"][box.uuid]["flags"][
                        flag.uuid
                    ] = {"name": flag.name}
        app.settings["scoreboard_state"] = game_state


def score_bots():
    """Award money for botnets"""
    logging.info("Scoring botnets, please wait ...")
    bot_manager = BotManager.instance()
    event_manager = EventManager.instance()
    for team in Team.all():
        if not team.locked:
            bots = bot_manager.by_team(team.name)
            if 0 < len(bots):
                reward = 0
                for bot in bots:
                    try:
                        reward += options.bot_reward
                        bot.write_message(
                            {
                                "opcode": "status",
                                "message": "Collected $%d reward" % options.bot_reward,
                            }
                        )
                    except:
                        logging.info(
                            "Bot at %s failed to respond to score ping" % bot.remote_ip
                        )

                message = "%s was awarded $%d for controlling %s bot(s)" % (
                    team.name,
                    reward,
                    len(bots),
                )
                bot_manager.add_rewards(team.name, options.bot_reward)
                bot_manager.notify_monitors(team.name)
                team.set_score("bot", reward + team.money)
                dbsession.add(team)
                dbsession.flush()
                event_manager.bot_scored(team, message)
    dbsession.commit()
