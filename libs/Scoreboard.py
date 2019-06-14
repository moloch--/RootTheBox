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

from models import dbsession
from models.Team import Team
from libs.BotManager import BotManager
from libs.EventManager import EventManager
from tornado.options import options
from builtins import object, str


class Scoreboard(object):
    """ Manages websocket connections (mostly thread safe) """

    @classmethod
    def now(self, app):
        """ Returns the current game state """
        game_state = {}
        for team in Team.all():
            if len(team.members) > 0:
                millis = int(round(time.time() * 1000))
                game_state[team.name] = {
                    "uuid": team.uuid,
                    "flags": [str(flag) for flag in team.flags],
                    "game_levels": [str(lvl) for lvl in team.game_levels],
                }
                highlights = {"money": 0, "flag": 0, "bot": 0, "hint": 0}
                for item in highlights:
                    value = team.get_score(item)
                    game_state[team.name][item] = value
                    game_history = app.settings["scoreboard_history"]
                    if team.name in game_history:
                        prev = game_history[team.name][item]
                        if prev < value:
                            highlights[item] = millis
                        else:
                            highlights[item] = game_history[team.name]["highlights"][
                                item
                            ]
                highlights["now"] = millis
                game_state[team.name]["highlights"] = highlights
                app.settings["scoreboard_history"][team.name] = game_state.get(
                    team.name
                )
        return json.dumps(game_state)


def score_bots():
    """ Award money for botnets """
    logging.info("Scoring botnets, please wait ...")
    bot_manager = BotManager.instance()
    event_manager = EventManager.instance()
    for team in Team.all():
        if len(team.members) > 0:
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
                team.money += reward
                dbsession.add(team)
                dbsession.flush()
                event_manager.bot_scored(team, message)
    dbsession.commit()
