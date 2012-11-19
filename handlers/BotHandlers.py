# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

@author: haddaway, moloch

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
import tornado.websocket

from libs.SecurityDecorators import debug
from libs.Sessions import MemcachedSession
from libs.ConfigManager import ConfigManager
from libs.EventManager import EventManager


class BotHandler(tornado.websocket.WebSocketHandler):
    ''' Handles websocket connections '''

    def initialize(self):
        self.event_manager = EventManager.Instance()
        self.config = ConfigManager.Instance()
        self.team = None
        self.box = None
        self.remote_ip = None

    @debug
    def is_active(self):
        return bool(self.box is not None and self.team is not None)

    @debug
    def open(self):
        ''' When we receive a new websocket connect '''
        box = Box.by_ip_address(self.request.remote_ip)
        if box is not None:
            self.box = box
            self.remote_ip = self.request.remote_ip
            self.write_message("box ok")
        else:
            self.close()

    @debug
    def on_message(self, message):
        ''' Troll the haxors '''
        team = User.by_handle(message)
        if team is not None:
            self.team = team
            self.write_message("team ok")
            self.manager.add_bot(self)
            self.manager.new_bot(self)
        else:
            self.write_message("Invalid hacker name.")
            self.close()

    @debug
    def on_close(self):
        ''' Lost connection to bot '''
        try:
            if is_active():
                self.manager.remove_bot(self)
        except KeyError:
            logging.warn("[Bot] Manager does not have a refrence to self.")
