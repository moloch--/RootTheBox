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

from models import Notification
from datetime import datetime
from libs.SecurityDecorators import *
from handlers.BaseHandlers import BaseHandler, BaseWebSocketHandler


class NotifySocketHandler(BaseWebSocketHandler):
    ''' Handles websocket connections '''

    def open(self):
        ''' When we receive a new websocket connect '''
        if self.session is not None and 'team_id' in self.session:
            logging.debug("[Web Socket] Opened new websocket with user id: %s" % (
                self.session['user_id'],
            ))
            notifications = Notification.new_messages(self.session['user_id'])
            logging.debug("[Web Socket] %d new notification(s) for user id %d" % (
                len(notifications), self.session['user_id']),
            )
            for notify in notifications:
                self.write_message(notify.to_json())
                Notification.delivered(notify.user_id, notify.event_uuid)
        else:
            logging.debug("[Web Socket] Opened public notification socket.")
        self.start_time = datetime.now()
        self.manager.add_connection(self)

    @property
    def team_id(self):
        if self.session is None or 'team_id' not in self.session:
            return '$public_team'
        else:
            return self.session['team_id']

    @team_id.setter
    def team_id(self, value):
        raise ValueError('Cannot set team_id')

    @property
    def user_id(self):
        return '$public_user' if self.session is None else self.session['user_id']

    @user_id.setter
    def user_id(self, value):
        raise ValueError('Cannot set user_id')

    @property
    def time_elapsed(self):
        return datetime.now() - self.start_time

    def on_close(self):
        ''' Lost connection to client '''
        try:
            self.manager.remove_connection(self)
        except KeyError:
            logging.warn("[Web Socket] Manager has no ref to self ???")


class AllNotificationsHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        self.render("notifications/view.html", user=user)