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


import logging
import pylibmc
import tornado.websocket

from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import debug
from libs.GameHistory import GameHistory
from libs.Sessions import MemcachedSession
from libs.ConfigManager import ConfigManager
from libs.Scoreboard import Scoreboard
from libs.EventManager import EventManager
from models import Team

class GameDataHandler(tornado.websocket.WebSocketHandler):
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
    '''
    Main summary page
    '''

    def get(self, *args, **kargs):
        self.render('scoreboard/summary.html')


class ScoreboardAjaxHandler(BaseHandler):

    def get(self, *args, **kargs):
        ''' Renders AJAX snippit based on URI '''
        uri = {
            'summary': self.summary_table,
        }
        if 1 == len(args) and args[0] in uri.keys():
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def summary_table(self):
        ''' Render the "leaderboard" snippit '''
        self.render('scoreboard/summary_table.html', teams=Team.ranks())


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
        if 1 == len(args) and args[0] in uri.keys():
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
        if 1 == len(args) and args[0] in uri.keys():
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def pie_chart(self):
        self.render('scoreboard/flags/pie_chart.html')

    def bar_chart(self):
        self.render('scoreboard/flags/bar_chart.html')