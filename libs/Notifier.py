# -*- coding: utf-8 -*-
'''
Created on Sep 20, 2012

@author: moloch

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


import threading

from libs.Singleton import Singleton
from models import dbsession, Notification, User, Team


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

    def refresh(self):
        ''' Non-blocking call '''
        threading.Thread(target=self.__refresh__).start()

    def add_connection(self, wsocket):
        ''' Add a connection '''
        self.lock.acquire()
        self.connections[wsocket.user_id] = wsocket
        self.lock.release()
        messages = Notification.new_messages(wsocket.user_id)
        for message in messages:
            wsocket.write_message(message.to_json())
            message.viewed = True
            dbsession.add(message)
            dbsession.flush()

    def remove_connection(self, wsocket):
        ''' Remove connection '''
        self.lock.acquire()
        del self.connections[wsocket.user_id]
        self.lock.release()

    def __refresh__(self):
        ''' Check for new notifications and send them to clients '''
        self.lock.acquire()
        connections = list(self.connections)
        self.lock.release()
        for wsocket in connections:
            messages = Notification.new_messages(wsocket.user_id)
            if 0 < len(messages):
                logging.debug("Sending %d notifications to user id %s." % (len(messages), str(wsocket.user_id)))
                for message in messages:
                    wsocket.write_message(message.to_json())
                    message.viewed = True
                    dbsession.add(message)
                    dbsession.flush()
            else:
                logging.debug("No new notification for user id %s" % str(wsocket.user_id))


class Notifier(object):
    ''' Handles the creation of notification objects '''

    @classmethod
    def ad_hoc_success(cls, user, title, message):
        ''' Create success notification for a single user '''
        cls.__create__(user, title, message, SUCCESS)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def team_success(cls, team, title, message):
        ''' Create success notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, SUCCESS)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def broadcast_success(cls, title, message):
        ''' Send a success notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, SUCCESS)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def ad_hoc_info(cls, user, title, message):
        ''' Create info notification for a single user '''
        cls.__create__(user, title, message, INFO)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def team_info(cls, team, title, message):
        ''' Create info notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, INFO)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def broadcast_info(cls, title, message):
        ''' Send a info notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, INFO)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def ad_hoc_warning(cls, user, title, message):
        ''' Create warning notification for a single user '''
        cls.__create__(user, title, message, WARNING)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def team_warning(cls, team, title, message):
        ''' Create warning notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, WARNING)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def broadcast_warning(cls, title, message):
        ''' Send a warning notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, WARNING)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def ad_hoc_error(cls, user, title, message):
        ''' Create error notification for a single user '''
        cls.__create__(user, title, message, ERROR)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def team_error(cls, team, title, message):
        ''' Create error notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, ERROR)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def broadcast_error(cls, title, message):
        ''' Send a error notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, ERROR)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def ad_hoc_custom(cls, user, title, message, icon):
        ''' Create custom notification for a single user '''
        cls.__create__(user, title, message, CUSTOM, icon)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def team_custom(cls, team, title, message, icon):
        ''' Create custom notification to each user on a team '''
        for user in team.members:
            cls.__create__(user, title, message, CUSTOM, icon)
        notifyManager = NotifyManager.Instance()
        notifyManager.refresh()

    @classmethod
    def broadcast_custom(cls, title, message, icon):
        ''' Send a custom notification to all users '''
        for user in User.all_users():
            cls.__create__(user, title, message, CUSTOM, icon)
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
        if icon != None:
            notification.icon = icon
        dbsession.add(notification)
        dbsession.flush()
