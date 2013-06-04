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

from uuid import uuid4
from libs.BotManager import BotManager
from models import Box, Team


BOX_OKAY  = 'box ok'
TEAM_OKAY = 'team ok'
AUTH_FAIL = 'auth fail'
AUTH_OKAY = 'auth ok'
XID       = 'xid:'


class BotHandler(tornado.websocket.WebSocketHandler):
    ''' Handles websocket connections '''

    def initialize(self):
        self.bot_manager = BotManager.Instance()
        self._team_uuid = None
        self.box_uuid = None
        self.remote_ip = None
        self.uuid = unicode(uuid4())

    def open(self, *args):
        ''' When we receive a new websocket connect '''
        box = Box.by_ip_address(self.request.remote_ip)
        if box is not None:
            self.box_uuid = ''.join(box.uuid)
            self.remote_ip = self.request.remote_ip
            self.write_message(BOX_OKAY)
        else:
            logging.debug("Rejected bot from '%s' (not a box)" % self.request.remote_ip)
            self.write_message(AUTH_FAIL)
            self.close()

    def on_message(self, message):
        logging.debug("Recv team uuid: %s" % message)
        self.team_uuid = message

    def on_close(self):
        ''' Close connection to remote host '''
        if self.uuid in self.bot_manager.botnet:
            self.bot_manager.remove_bot(self)
        logging.debug("Closing connection to bot at %s" % self.request.remote_ip)

    @property
    def team_uuid(self):
        return self._team_uuid

    @team_uuid.setter
    def team_uuid(self, team_uuid):
        if self._team_uuid is not None:
            logging.warn("Botnet protocol breach; set team uuid twice")
            self.close()
        else:
            team = Team.by_uuid(team_uuid)
            if team is None:
                logging.debug("Auth fail, invalid team uuid")
                self.write_message(AUTH_FAIL)
                self.close()
            else:
                self._team_uuid = team.uuid
                logging.debug("Team %s owns bot: %s" % (team.name, self.uuid))
                self.init_success()

    def init_success(self):
        if self.bot_manager.add_bot(self):
            logging.debug("Auth okay, adding '%s' to botnet" % self.uuid)
            self.write_message(AUTH_OKAY)
        else:
            logging.debug("Auth fail; duplicate bot")
            self.write_message(AUTH_FAIL)
            self.close()
