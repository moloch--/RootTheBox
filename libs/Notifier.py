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

from uuid import uuid4
from libs.Singleton import Singleton
from libs.SecurityDecorators import async
from models import dbsession, Notification, User


### Constants ###
SUCCESS = u"success"
INFO = u"info"
WARNING = u"warning"
ERROR = u"error"
CUSTOM = u"custom"

class Notifier(object):
    ''' Handles the creation of notification objects '''

    @classmethod
    def user_success(cls, user, title, message):
        ''' Create success notification for a single user '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, SUCCESS, event_uuid)
        cls.__create__(user, title, message, SUCCESS, event_uuid)
        return event_uuid

    @classmethod
    def team_success(cls, team, title, message):
        ''' Create success notification to each user on a team '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, SUCCESS, event_uuid)
        for user in team.members:
            cls.__create__(user, title, message, SUCCESS, event_uuid)
        return event_uuid

    @classmethod
    def broadcast_success(cls, title, message):
        ''' Send a success notification to all users '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, SUCCESS, event_uuid)
        for user in User.all_users():
            cls.__create__(user, title, message, SUCCESS, event_uuid)
        return event_uuid

    @classmethod
    def user_info(cls, user, title, message):
        ''' Create info notification for a single user '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, INFO, event_uuid)
        cls.__create__(user, title, message, INFO, event_uuid)
        return event_uuid

    @classmethod
    def team_info(cls, team, title, message):
        ''' Create info notification to each user on a team '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, INFO, event_uuid)
        for user in team.members:
            cls.__create__(user, title, message, INFO, event_uuid)
        return event_uuid

    @classmethod
    def broadcast_info(cls, title, message):
        ''' Send a info notification to all users '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, INFO, event_uuid)
        for user in User.all_users():
            cls.__create__(user, title, message, INFO, event_uuid)
        return event_uuid

    @classmethod
    def user_warning(cls, user, title, message):
        ''' Create warning notification for a single user '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, WARNING, event_uuid)
        cls.__create__(user, title, message, WARNING, event_uuid)
        return event_uuid

    @classmethod
    def team_warning(cls, team, title, message):
        ''' Create warning notification to each user on a team '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, WARNING, event_uuid)
        for user in team.members:
            cls.__create__(user, title, message, WARNING, event_uuid)
        return event_uuid

    @classmethod
    def broadcast_warning(cls, title, message):
        ''' Send a warning notification to all users '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, WARNING, event_uuid)
        for user in User.all_users():
            cls.__create__(user, title, message, WARNING, event_uuid)
        return event_uuid

    @classmethod
    def user_error(cls, user, title, message):
        ''' Create error notification for a single user '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, ERROR, event_uuid)
        cls.__create__(user, title, message, ERROR, event_uuid)
        return event_uuid

    @classmethod
    def team_error(cls, team, title, message):
        ''' Create error notification to each user on a team '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, ERROR, event_uuid)
        for user in team.members:
            cls.__create__(user, title, message, ERROR, event_uuid)
        return event_uuid

    @classmethod
    def broadcast_error(cls, title, message):
        ''' Send a error notification to all users '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(user, title, message, ERROR, event_uuid, icon)
        for user in User.all_users():
            cls.__create__(user, title, message, ERROR, event_uuid)
        return event_uuid

    @classmethod
    def user_custom(cls, user, title, message, icon):
        ''' Create custom notification for a single user '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(user, title, message, CUSTOM, event_uuid, icon)
        cls.__create__(user, title, message, CUSTOM, event_uuid, icon)
        return event_uuid

    @classmethod
    def team_custom(cls, team, title, message, icon):
        ''' Create custom notification to each user on a team '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, CUSTOM, event_uuid, icon)
        for user in team.members:
            cls.__create__(user, title, message, CUSTOM, event_uuid, icon)
        return event_uuid

    @classmethod
    def broadcast_custom(cls, title, message, icon):
        ''' Send a custom notification to all users '''
        event_uuid = unicode(uuid4())
        cls.__anonymous__(title, message, CUSTOM, event_uuid, icon)
        for user in User.all_users():
            cls.__create__(user, title, message, CUSTOM, event_uuid, icon)
        return event_uuid

    @classmethod
    def __anonymous__(cls, title, message, category, event_uuid, icon=None):
        ''' Creates anonysmous notification where user_id = NULL '''
        notification = Notification(
            user_id=None,
            event_uuid=event_uuid,
            title=unicode(title),
            message=unicode(message),
            category=category,
        )
        if icon is not None:
            notification.icon = icon
        dbsession.add(notification)
        dbsession.flush()

    @classmethod
    def __create__(cls, user, title, message, category, event_uuid, icon=None):
        ''' Create a notification and save it to the database '''
        notification = Notification(
            user_id=user.id,
            event_uuid=event_uuid,
            title=unicode(title),
            message=unicode(message),
            category=category,
        )
        if icon is not None:
            notification.icon = icon
        dbsession.add(notification)
        dbsession.flush()
