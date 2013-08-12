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


import json
import logging
import tornado.websocket


from uuid import uuid4
from libs.BotManager import BotManager
from libs.EventManager import EventManager
from models import Box, Team, User
from models.User import ADMIN_PERMISSION
from BaseHandlers import BaseHandler
from libs.SecurityDecorators import authenticated


class BotSocketHandler(tornado.websocket.WebSocketHandler):
    ''' Handles websocket connections '''

    def initialize(self):
        self.bot_manager = BotManager.Instance()
        self.event_manager = EventManager.Instance()
        self.team_name = None
        self.team_uuid = None
        self.box_uuid = None
        self.remote_ip = None
        self.uuid = unicode(uuid4())
        self.opcodes = {
            'set_user': self.set_user,
        }
    
    def open(self, *args):
        ''' When we receive a new websocket connect '''
        box = Box.by_ip_address(self.request.remote_ip)
        if box is not None:
            self.box_uuid = box.uuid
            self.box_name = box.name
            self.remote_ip = self.request.remote_ip
            self.write_message({
                'opcode': 'get_user',
            })
        else:
            logging.debug("Rejected bot from '%s' (not a box)" % self.request.remote_ip)
            self.write_message({
                'opcode': 'error',
                'message': 'Invalid IP address.'
            })
            self.close()

    def on_message(self, message):
        ''' Parse request '''
        try:
            req = json.loads(message)
            if 'opcode' not in req:
                raise ValueError('Missing opcode')
            elif req['opcode'] not in self.opcodes:
                raise ValueError('Invalid opcode in request: %s' % req['opcode'])
            else:
                self.opcodes[req['opcode']](req)
        except ValueError as error:
            logging.warn("Invalid json request from bot: %s" % str(error))

    def on_close(self):
        ''' Close connection to remote host '''
        if self.uuid in self.bot_manager.botnet:
            self.bot_manager.remove_bot(self)
        logging.debug("Closing connection to bot at %s" % self.request.remote_ip)

    def set_user(self, req):
        ''' Get user details '''
        if self.team_uuid is not None:
            self.write_message({
                'opcode': 'error',
                'message': 'User is already set'
            })
            self.close()
        else:
            user = User.by_handle(req['user'])
            if user is None or user.has_permission(ADMIN_PERMISSION):
                logging.debug("Received invalid user '%s' from bot on %s" % (
                    req['user'], self.remote_ip,
                ))
                self.write_message({
                    'opcode': 'error',
                    'message': 'Hacker does not exist'
                })
                self.close()
            else:
                self.write_message({
                    'opcode': 'status',
                    'message': 'Found user "%s"' % user.handle,
                })
                self.set_team(user.team)

    def set_team(self, team):
        ''' Set team based on user '''
        if team is None:
            logging.debug("Auth fail, invalid team uuid")
            self.write_message({
                'opcode': 'error',
                'message': 'Team does not exist'
            })
            self.close()
        else:
            self.team_uuid = team.uuid
            self.team_name = team.name
            logging.debug("'%s' owns bot: %s" % (team.name, self.uuid))
            self.init_success()

    def init_success(self):
        if self.bot_manager.add_bot(self):
            logging.debug("Auth okay, adding '%s' to botnet" % self.uuid)
            count = self.bot_manager.count_by_team(self.team_name)
            self.write_message({
                'opcode': 'status',
                'message': 'Added new bot; total number of bots is now %d' % count
            })
        else:
            logging.debug("Auth failed, duplicate bot on %s" % self.remote_ip)
            self.write_message({
                'opcode': 'error',
                'message': 'Duplicate bot'
            })
            self.close()


class BotMonitorHandler(tornado.websocket.WebSocketHandler):
    ''' Handles BotMonitor websocket connections '''

    def initialize(self):
        self.bot_manager = BotManager.Instance()
        self.team_name = None
        self.uuid = unicode(uuid4())
        self.opcodes = {
            'auth': self.auth,
        }

    def open(self):
        logging.debug("Opened new monitor socket to %s" % self.request.remote_ip)

    def on_message(self, message):
        ''' Parse request '''
        try:
            req = json.loads(message)
            if 'opcode' not in req:
                raise ValueError('Missing opcode')
            elif req['opcode'] not in self.opcodes:
                raise ValueError('Invalid opcode in request: %s' % req['opcode'])
            else:
                self.opcodes[req['opcode']](req)
        except ValueError as error:
            logging.warn("Invalid json request from bot: %s" % str(error))

    def on_close(self):
        ''' Close connection to remote host '''
        self.bot_manager.remove_monitor(self)
        logging.debug("Closing connection to bot monitor at %s" % self.request.remote_ip)

    def auth(self, req):
        ''' Authenticate user '''
        try:
            user = User.by_handle(req['handle'])
        except:
            user = None
        if user is None or user.has_permission(ADMIN_PERMISSION):
            logging.debug("Monitor socket user does not exist.")
            self.write_message({
                'opcode': 'auth_failure',
                'message': 'Authentication failure',
            })
            self.close()
        elif user.validate_password(req.get('password', '')):
            logging.debug("Monitor socket successfully authenticated as %s" % user.handle)
            self.team_name = ''.join(user.team.name)
            self.bot_manager.add_monitor(self)
            self.write_message({'opcode': 'auth_success'})
            boxes = self.bot_manager.get_boxes(self.team_name)
            self.update(boxes)
        else:
            logging.debug("Monitor socket provided invalid password for user")
            self.write_message({
                'opcode': 'auth_failure',
                'message': 'Authentication failure',
            })
            self.close()

    def update(self, boxes):
        ''' Update state information '''
        self.write_message({'opcode': 'update', 'boxes': boxes})
