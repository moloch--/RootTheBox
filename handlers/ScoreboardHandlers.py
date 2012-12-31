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
import pylibmc


from tornado.websocket import WebSocketHandler
from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import debug
from libs.GameHistory import GameHistory
from libs.Sessions import MemcachedSession
from libs.ConfigManager import ConfigManager
from libs.Scoreboard import Scoreboard
from libs.EventManager import EventManager
from models import Team


class GameDataHandler(WebSocketHandler):
    '''
    Get Score data via websocket
    '''

    def initialize(self):
        ''' Setup sessions '''
        self.manager = EventManager.Instance()

    @debug
    def open(self):
        ''' When we receive a new websocket connect '''
        self.manager.scoreboard_connections.append(self)
        self.write_message(self.manager.scoreboard.now())

    @debug
    def on_message(self, message):
        ''' Send current state '''
        pass

    @debug
    def on_close(self):
        ''' Lost connection to client '''
        try:
            self.manager.scoreboard_connections.remove(self)
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
        if 1 == len(args) and args[0] in uri:
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
                    'captured': [flag.name for flag in team.level_flags(lvl.number)],
                    'total': len(lvl.flags),
                }
                details['game_levels'].append(lvl_details)
            self.write(details)
        else:
            self.write({'error': 'Team does not exist'})
        self.finish()


class ScoreboardMoneyHandler(BaseHandler):
    '''
    Renders money-spec pages
    '''

    def get(self, *args, **kargs):
        ''' Render pie chart '''
        uri = {
            'pie_chart': self.pie_chart,
            'bar_chart': self.bar_chart,
        }
        if 1 == len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def pie_chart(self):
        self.render('scoreboard/money/pie_chart.html')

    def bar_chart(self):
        self.render('scoreboard/money/bar_chart.html')


class ScoreboardFlagHandler(BaseHandler):
    '''
    Renders flag-spec pages
    '''

    def get(self, *args, **kargs):
        ''' Render pie chart '''
        uri = {
            'pie_chart': self.pie_chart,
            'bar_chart': self.bar_chart,
        }
        if 1 == len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def pie_chart(self):
        self.render('scoreboard/flags/pie_chart.html')

    def bar_chart(self):
        self.render('scoreboard/flags/bar_chart.html')


class ScoreboardHistoryHandler(BaseHandler):

    def get(self, *args, **kwargs):
        uri = {
            'money': self.money,
            'flags': self.flags,
        }
        if 1 == len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def money(self):
        game_history = GameHistory.Instance()
        history = {}
        for team in Team.all():
            history[team.name] = game_history.get_money_history_by_name(team.name, -30)
        self.render('scoreboard/history/money.html', history=history)

    def flags(self):
        game_history = GameHistory.Instance()
        history = {}
        for team in Team.all():
            history[team.name] = game_history.get_flag_history_by_name(team.name, -30)
        self.render('scoreboard/history/flags.html', history=history)


class ScoreboardHistorySocketHandler(WebSocketHandler):

    def initialize(self):
        ''' Setup sessions '''
        self.manager = EventManager.Instance()
        self.game_history = GameHistory.Instance()

    @debug
    def open(self):
        ''' When we receive a new websocket connect '''
        self.manager.history_connections.append(self)
        self.write_message(self.get_history())

    @debug
    def on_message(self, message):
        ''' Send current state '''
        try:
            count = int(message)
            if len(self.game_history) < count:
                count = len(self.game_history)
            self.write_message({'history': self.get_history(count)})
        except ValueError:
            self.write_message({'error': 'Not a number'})
        except:
            self.write_message({'error': "Something didn't work ..."})

    @debug
    def on_close(self):
        ''' Lost connection to client '''
        try:
            self.manager.history_connections.remove(self)
        except KeyError:
            logging.warn("[Web Socket] Connection has already been closed.")

    def get_history(self, length=9):
        ''' Send history in JSON '''
        length = abs(length) + 1
        return json.dumps({'history': self.game_history[(-1 * length):]})