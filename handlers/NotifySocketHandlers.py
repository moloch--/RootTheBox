# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

@author: haddaway, moloch

    Copyright [2012] [Redacted Labs]

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


import pylibmc
import logging
import tornado.websocket

from libs.SecurityDecorators import *
from libs.Notifier import NotifyManager
from libs.Sessions import MemcachedSession
from libs.ConfigManager import ConfigManager


class NotifySocketHandler(tornado.websocket.WebSocketHandler):
    ''' Handles websocket connections '''

    def initialize(self):
        self.session = None
        self.manager = NotifyManager.Instance()
        self.config = ConfigManager.Instance()
        session_id = self.get_secure_cookie('session_id')
        if session_id != None:
            self.conn = pylibmc.Client(
                [self.config.memcached_server], binary=True)
            self.conn.behaviors['no_block'] = 1  # async I/O
            self.session = self._create_session(session_id)
            self.session.refresh()

    def _create_session(self, session_id=None):
        ''' Creates a new session '''
        kw = {
            'duration': self.config.session_age,
            'ip_address': self.request.remote_ip,
            'regeneration_interval': self.config.session_regeneration_interval,
        }
        new_session = None
        old_session = None
        old_session = MemcachedSession.load(session_id, self.conn)
        if old_session is None or old_session._is_expired():  # Create new session
            new_session = MemcachedSession(self.conn, **kw)
        if old_session is not None:
            if old_session._should_regenerate():
                old_session.refresh(new_session_id=True)
                logging.debug(" *** Refreshing Session ***")
            return old_session
        return new_session

    def open(self):
        ''' When we recieve a new websocket connect '''
        if self.session != None:
            logging.debug("Opened new websocket with user id: %s" % str(self.session['user_id']))
            self.user_id = self.session['user_id']
            self.manager.add_connection(self)
        else:
            logging.debug("NotifySocketHandler recieved no session data.")

    def on_message(self, message):
        ''' Troll the haxors '''
        self.write_message("ERROR 1146 (42S02): Table 'rtb.%s' doesn't exist." % message) # Hehe

    def on_close(self):
        ''' Lost connection to client '''
        self.manager.remove_connection(self)
