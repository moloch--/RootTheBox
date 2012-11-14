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
from libs.GameHistory import GameHistory
from libs.Sessions import MemcachedSession
from libs.ConfigManager import ConfigManager
from libs.Scoreboard import ScoreboardManager
from models import Team

class GameDataHandler(tornado.websocket.WebSocketHandler):
    '''
    Get Score data via websocket
    '''

    def initialize(self):
        ''' Setup sessions '''
        self.session = None
        self.scoreboard_manager = ScoreboardManager.Instance()
        self.config = ConfigManager.Instance()
        session_id = self.get_secure_cookie('session_id')
        if session_id != None:
            self.conn = pylibmc.Client(
                [self.config.memcached_server], binary=True)
            self.conn.behaviors['no_block'] = 1  # Async I/O
            self.session = self._create_session(session_id)
            self.session.refresh()


    def _create_session(self, session_id=None):
        ''' Creates a new session '''
        kwargs = {
            'duration': self.config.session_age,
            'ip_address': self.request.remote_ip,
            'regeneration_interval': self.config.session_regeneration_interval,
        }
        new_session = None
        old_session = MemcachedSession.load(session_id, self.conn)
        if old_session is None or old_session._is_expired():
            new_session = MemcachedSession(self.conn, **kwargs)
        if old_session is not None:
            if old_session._should_regenerate():
                old_session.refresh()
            return old_session
        return new_session

    def open(self):
        ''' When we receive a new websocket connect '''
        if self.session != None:
            logging.debug("Opened new websocket with user id: %s" % str(self.session['user_id']))
            self.user_id = self.session['user_id']
            self.scoreboard_manager.add_connection(self)
        else:
            self.user_id = 'public'
            self.scoreboard_manager.add_connection(self)
        self.write_message(self.scoreboard_manager.now())

    def on_message(self, message):
        ''' Send current state '''
        self.write_message(self.scoreboard_manager.now())

    def on_close(self):
        ''' Lost connection to client '''
        try:
            self.scoreboard_manager.remove_connection(self)
        except KeyError:
            logging.warn("WebSocket connection has already been closed.")


class ScoreboardHandler(BaseHandler):

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
        self.render('scoreboard/summary_table.html', teams=Team.all())


class ScoreboardMoneyHandler(BaseHandler):
    '''
    Renders real-time scoreboard pages
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
    Renders real-time scoreboard pages
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