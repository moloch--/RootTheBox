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
----------------------------------------------------------------------------

This file contains handlers related to the scoreboard.

'''


import json
import logging

from tornado.websocket import WebSocketHandler
from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import use_black_market
from libs.GameHistory import GameHistory
from libs.Scoreboard import Scoreboard
from models.Team import Team
from models.WallOfSheep import WallOfSheep
from datetime import datetime, timedelta


class ScoreboardDataSocketHandler(WebSocketHandler):
    ''' Get Score data via websocket '''

    connections = set()

    def initialize(self):
        self.last_message = datetime.now()

    def open(self):
        ''' When we receive a new websocket connect '''
        self.connections.add(self)
        self.write_message(Scoreboard.now())

    def on_message(self, message):
        ''' We ignore messages if there are more than 1 every 5 seconds '''
        if self.last_message - datetime.now() > timedelta(seconds=5):
            self.last_message = datetime.now()
            self.write_message(Scoreboard.now())

    def on_close(self):
        ''' Lost connection to client '''
        try:
            self.connections.remove(self)
        except KeyError:
            logging.warn("[Web Socket] Connection has already been closed.")


class ScoreboardHandler(BaseHandler):
    ''' Main summary page '''

    def get(self, *args, **kargs):
        self.render('scoreboard/summary.html')


class ScoreboardAjaxHandler(BaseHandler):

    def get(self, *args, **kargs):
        ''' Renders AJAX snippit based on URI '''
        uri = {
            'summary': self.summary_table,
            'team': self.team_details,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def summary_table(self):
        ''' Render the "leaderboard" snippit '''
        self.render('scoreboard/summary_table.html', teams=Team.ranks())

    def team_details(self):
        ''' Returns team details in JSON form '''
        uuid = self.get_argument('uuid', '')
        team = Team.by_uuid(uuid)
        if team is not None:
            details = {
                'name': team.name,
                'game_levels': [],
            }
            for lvl in team.levels:
                lvl_details = {
                    'number': lvl.number,
                    'captured':
                        [flag.name for flag in team.level_flags(lvl.number)],
                    'total': len(lvl.flags),
                }
                details['game_levels'].append(lvl_details)
            self.write(details)
        else:
            self.write({'error': 'Team does not exist'})
        self.finish()


class ScoreboardHistoryHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('scoreboard/history.html')


class ScoreboardHistorySocketHandler(WebSocketHandler):

    connections = set()
    game_history = GameHistory.instance()

    def initialize(self):
        self.last_message = datetime.now()

    def open(self):
        ''' When we receive a new websocket connect '''
        self.connections.add(self)
        self.write_message(self.get_history())

    def on_message(self, message):
        ''' We ignore messages if there are more than 1 every 5 seconds '''
        if self.last_message - datetime.now() > timedelta(seconds=5):
            self.last_message = datetime.now()
            self.write_message(self.game_history[:-1])

    def on_close(self):
        ''' Lost connection to client '''
        self.connections.remove(self)

    def get_history(self, length=29):
        ''' Send history in JSON '''
        length = abs(length) + 1
        return json.dumps({'history': self.game_history[(-1 * length):]})


class ScoreboardWallOfSheepHandler(BaseHandler):

    @use_black_market
    def get(self, *args, **kwargs):
        ''' Optionally order by argument; defaults to date/time '''
        order = self.get_argument('order_by', '').lower()
        if order == 'prize':
            sheep = WallOfSheep.all_order_value()
        elif order == 'length':
            sheep = sorted(WallOfSheep.all())
        else:
            sheep = WallOfSheep.all_order_created()
        leaderboard = WallOfSheep.leaderboard()
        self.render('scoreboard/wall_of_sheep.html',
                    leaderboard=leaderboard,
                    flock=sheep)


class TeamsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render('scoreboard/teams.html')
