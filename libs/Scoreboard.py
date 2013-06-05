# -*- coding: utf-8 -*-

'''
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
'''


import json
import logging

from models import Team, GameSettings, dbsession
from libs.BotManager import BotManager
from libs.ConfigManager import ConfigManager


class Scoreboard(object):
    ''' Manages websocket connections (mostly thread safe) '''

    def now(self):
        ''' Returns the current game state '''
        game_state = {}
        for team in Team.all():
            game_state[team.name] = {
                'money': team.money,
                'flags': [str(flag) for flag in team.flags],
                'game_levels': [str(lvl) for lvl in team.game_levels],
            }
        return json.dumps(game_state)


def score_bots():
    ''' Award money for botnets '''
    logging.info("Scoring botnets, please wait ...")
    bot_manager = BotManager.Instance()
    game_settings = GameSettings.get_active()
    for team in Team.all():
        bot_count = bot_manager.count_by_team_uuid(team.uuid)
        if 0 < bot_count:
            reward = game_settings.bot_reward * bot_count
            logging.debug("%s was awarded $%d for controlling %s bot(s)" % (
                team.name, reward, bot_count,
            ))
            team.money += reward
            dbsession.add(team)
            dbsession.flush()
