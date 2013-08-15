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

from models import Team, dbsession
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
    config = ConfigManager.Instance()
    for team in Team.all():
        bots = bot_manager.by_team(team.name)
        reward = 0
        for bot in bots:
            try:
                reward += config.bot_reward
                bot.write_message({
                    'opcode': 'status',
                    'message': 'Collected $%d reward' % config.bot_reward
                })
            except:
                logging.info(
                    "Bot at %s failed to respond to score ping" % bot.remote_ip
                )
        if 0 < len(bots):
            logging.debug("%s was awarded $%d for controlling %s bot(s)" % (
                team.name, reward, len(bots),
            ))
            bot_manager.add_rewards(team.name, config.bot_reward)
            bot_manager.notify_monitors(team.name)
            team.money += reward
            dbsession.add(team)
            dbsession.flush()
