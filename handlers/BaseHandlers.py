# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

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

This file contains the base handler, all other handlers (aside from
web socket handlers) should inherit from this base class.

'''


import logging
import pylibmc

from models import User
from libs.ConfigManager import ConfigManager
from libs.SecurityDecorators import *
from libs.Sessions import MemcachedSession
from libs.EventManager import EventManager
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler


class BaseHandler(RequestHandler):
    ''' User handlers extend this class '''

    def initialize(self):
        self.session = None
        self.new_events = []
        self.event_manager = self.application.settings['event_manager']
        self.config = ConfigManager.Instance()
        session_id = self.get_secure_cookie('session_id')
        if session_id is not None:
            self.conn = pylibmc.Client(
                [self.config.memcached_server],
                binary=True
            )
            self.conn.behaviors['no_block'] = 1  # async I/O
            self.session = self._create_session(session_id)
            self.session.refresh()

    def get_current_user(self):
        ''' Get current user object from database '''
        if self.session is not None:
            try:
                return User.by_uuid(self.session['user_uuid'])
            except KeyError:
                logging.exception(
                    "Malformed session: %r" % self.session
                )
            except:
                logging.exception("Failed call to get_current_user()")
        return None

    def start_session(self):
        ''' Starts a new session '''
        self.conn = pylibmc.Client(
            [self.config.memcached_server],
            binary=True,
        )
        self.conn.behaviors['no_block'] = 1  # async I/O
        self.session = self._create_session()
        self.set_secure_cookie('session_id',
            self.session.session_id,
            expires_days=1,
            expires=self.session.expires,
            path='/',
            HttpOnly=True,
        )

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
                old_session.refresh(new_session_id=True)
            return old_session
        return new_session

    def set_default_headers(self):
        ''' Set clickjacking/xss headers '''
        self.set_header("Server", "'; DROP TABLE servertypes; --")
        self.add_header("X-Frame-Options", "DENY")
        self.add_header("X-XSS-Protection", "1; mode=block")

    def get(self, *args, **kwargs):
        ''' Placeholder, incase child class does not impl this method '''
        self.render("public/404.html")

    def post(self, *args, **kwargs):
        ''' Placeholder, incase child class does not impl this method '''
        self.render("public/404.html")

    def put(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use PUT method" % self.request.remote_ip
        )
        self.render("public/404.html")

    def delete(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use DELETE method" % self.request.remote_ip
        )
        self.render("public/404.html")

    def head(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use HEAD method" % self.request.remote_ip
        )
        self.render("public/404.html")

    def options(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use OPTIONS method" % self.request.remote_ip
        )
        self.render("public/404.html")

    def on_finish(self, *args, **kwargs):
        if 0 < len(self.new_events):
            self._fire_events()

    def _fire_events(self):
        ''' Fire new events '''
        for event in self.new_events:
            assert(2 == len(event))
            event[0](**event[1])


class BaseWebSocketHandler(WebSocketHandler):
    ''' Handles websocket connections '''

    def initialize(self):
        self.session = None
        self.manager = EventManager.Instance()
        self.config = ConfigManager.Instance()
        session_id = self.get_secure_cookie('session_id')
        if session_id is not None:
            self.conn = pylibmc.Client(
                [self.config.memcached_server], 
                binary=True
            )
            self.conn.behaviors['no_block'] = 1  # async I/O
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
        old_session = None
        old_session = MemcachedSession.load(session_id, self.conn)
        if old_session is None or old_session._is_expired():
            new_session = MemcachedSession(self.conn, **kwargs)
        if old_session is not None:
            return old_session
        return new_session

    def get_current_user(self):
        ''' Get current user object from database '''
        if self.session is not None:
            try:
                return User.by_handle(self.session['handle'])
            except KeyError:
                logging.exception(
                    "Malformed session: %r" % self.session
                )
            except:
                logging.exception("Failed call to get_current_user()")
        return None

    def open(self):
        pass

    def on_message(self, message):
        pass

    def on_close(self):
        pass