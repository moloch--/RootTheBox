# -*- coding: utf-8 -*-
"""
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
"""

import logging

from libs.SecurityDecorators import *
from libs.EventManager import EventManager
from handlers.BaseHandlers import BaseHandler, BaseWebSocketHandler


class NotifySocketHandler(BaseWebSocketHandler):

    """Handles websocket connections"""

    event_manager = EventManager.instance()

    def open(self):
        """When we receive a new websocket connect"""
        self.event_manager.add_connection(self)
        if self.session is not None and "team_id" in self.session:
            logging.debug(
                "Opened new websocket with user id: %s" % (self.session["user_id"],)
            )
            self.io_loop.add_callback(
                self.event_manager.push_user, self.team_id, self.user_id
            )
        else:
            logging.debug("[Web Socket] Opened public notification socket.")

    def on_close(self):
        """Lost connection to client"""
        self.event_manager.remove_connection(self)

    @property
    def team_id(self):
        if self.session is not None and "team_id" in self.session:
            return self.session["team_id"]

    @team_id.setter
    def team_id(self, value):
        raise ValueError("Cannot set team_id")

    @property
    def user_id(self):
        if self.session is not None and "user_id" in self.session:
            return self.session["user_id"]

    @user_id.setter
    def user_id(self, value):
        raise ValueError("Cannot set user_id")


class AllNotificationsHandler(BaseHandler):
    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        self.render("notifications/view.html", user=user)
