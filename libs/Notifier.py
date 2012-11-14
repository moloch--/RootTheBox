# -*- coding: utf-8 -*-
'''
Created on Sep 20, 2012

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
import threading

from libs.Singleton import Singleton
from libs.SecurityDecorators import async
from models import dbsession, Notification, User


### Constants ###
SUCCESS = u"success"
INFO = u"info"
WARNING = u"warning"
ERROR = u"error"
CUSTOM = u"custom"


@Singleton
class NotifyManager(object):
    ''' Manages websocket connections (mostly thread safe) '''

    connections = {}

    def __init__(self):
        self.lock = threading.Lock()

    def add_connection(self, wsocket):
        ''' Add a connection '''
        self.lock.acquire()
        if self.connections.has_key(wsocket.user_id):
            self.connections[wsocket.user_id].append(wsocket)
        else:
            self.connections[wsocket.user_id] = [wsocket]
        self.lock.release()
        messages = Notification.new_messages(wsocket.user_id)
        for message in messages:
            self.__send__(message, self.connections[wsocket.user_id])

    def remove_connection(self, wsocket):
        ''' Remove connection '''
        self.lock.acquire()
        self.connections[wsocket.user_id].remove(wsocket)
        if len(self.connections[wsocket.user_id]) <= 0:
            del self.connections[wsocket.user_id]
        self.lock.release()

    #@async
    def refresh(self):
        ''' Check for new notifications and send them to clients '''
        self.lock.acquire()
        connections = dict(self.connections)
        self.lock.release()
        for user_id in connections.keys():
            try:
                logging.debug("Looking for notification for user id: %s" % str(user_id))
                messages = Notification.new_messages(user_id)
                if 0 < len(messages):
                    logging.debug("Sending %d notification(s) to user id %s." % (len(messages), str(user_id)))
                    wsockets = connections[user_id]
                    for message in messages:
                        message = Notification.by_id(message.id) # Refresh object, to avoid stale data
                        self.__send__(message, wsockets)
                else:
                    logging.debug("No new notifications for user id %s." % str(user_id))
            except:
                logging.exception("Exception while writing notification to websocket.")

    def __send__(self, message, wsockets):
        ''' Send a message to all websockets '''
        for wsocket in wsockets:
            wsocket.write_message(message.to_json())
        message.viewed = True
        dbsession.add(message)
        dbsession.flush()


class Notifier(object):
    ''' Handles the creation of notification objects '''

    @classmethod
    def user_success(cls, user, title, message):
        ''' Create success notification for a single user '''
        cls.__create__(user, title, message, SUCCESS)
        cls.__refresh__()

    @classmethod
    def team_success(cls, team, title, message):
        ''' Create success notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, SUCCESS)
        cls.__refresh__()

    @classmethod
    def broadcast_success(cls, title, message):
        ''' Send a success notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, SUCCESS)
        cls.__refresh__()

    @classmethod
    def user_info(cls, user, title, message):
        ''' Create info notification for a single user '''
        cls.__create__(user, title, message, INFO)
        cls.__refresh__()

    @classmethod
    def team_info(cls, team, title, message):
        ''' Create info notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, INFO)
        cls.__refresh__()

    @classmethod
    def broadcast_info(cls, title, message):
        ''' Send a info notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, INFO)
        cls.__refresh__()

    @classmethod
    def user_warning(cls, user, title, message):
        ''' Create warning notification for a single user '''
        cls.__create__(user, title, message, WARNING)
        cls.__refresh__()

    @classmethod
    def team_warning(cls, team, title, message):
        ''' Create warning notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, WARNING)
        cls.__refresh__()

    @classmethod
    def broadcast_warning(cls, title, message):
        ''' Send a warning notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, WARNING)
        cls.__refresh__()

    @classmethod
    def user_error(cls, user, title, message):
        ''' Create error notification for a single user '''
        cls.__create__(user, title, message, ERROR)
        cls.__refresh__()

    @classmethod
    def team_error(cls, team, title, message):
        ''' Create error notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, ERROR)
        cls.__refresh__()

    @classmethod
    def broadcast_error(cls, title, message):
        ''' Send a error notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, ERROR)
        cls.__refresh__()

    @classmethod
    def user_custom(cls, user, title, message, icon):
        ''' Create custom notification for a single user '''
        cls.__create__(user, title, message, CUSTOM, icon)
        cls.__refresh__()

    @classmethod
    def team_custom(cls, team, title, message, icon):
        ''' Create custom notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, CUSTOM, icon)
        cls.__refresh__()

    @classmethod
    def broadcast_custom(cls, title, message, icon):
        ''' Send a custom notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, CUSTOM, icon)
        cls.__refresh__()

    @classmethod
    def __refresh__(cls):
        ''' Refresh websocket manager '''
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def __create__(cls, user, title, message, category, icon=None):
        ''' Create a notification and save it to the database '''
        notification = Notification(
            user_id=user.id,
            title=unicode(title),
            message=unicode(message),
            category=category,
        )
        if icon is not None:
            notification.icon = icon
        dbsession.add(notification)
        dbsession.flush()
