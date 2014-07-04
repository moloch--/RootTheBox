# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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


import os
import json
import imghdr

from urlparse import urlparse
from uuid import uuid4
from libs.SecurityDecorators import debug
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.sql import and_
from sqlalchemy.types import Unicode, String, Integer, Boolean
from models import dbsession
from models.BaseModels import DatabaseObject

### Constants ###
SUCCESS = u"success"
INFO = u"info"
WARNING = u"warning"
ERROR = u"error"
CUSTOM = u"custom"


class Notification(DatabaseObject):
    ''' Notification definition '''

    user_id = Column(Integer, ForeignKey('user.id'))
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    event_uuid = Column(Unicode(36), nullable=False)
    title = Column(Unicode(256), nullable=False)
    message = Column(Unicode(256), nullable=False)
    viewed = Column(Boolean, default=False)
    icon_url = Column(Unicode(256), nullable=True)
    category = Column(Unicode(64), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).filter_by(user_id=None).all()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Returns a the object with id of _uuid '''
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_user_id(cls, _id):
        ''' Return notifications for a single user '''
        return dbsession.query(cls).filter_by(user_id=_id).order_by(desc(cls.created)).all()

    @classmethod
    def new_messages(cls, user_id):
        ''' Return all notification which have not been viewed '''
        return dbsession.query(cls).filter(
            and_(cls.user_id == user_id, cls.viewed == False)
        ).all()

    @classmethod
    def by_event_uuid(cls, uuid):
        ''' Always returns anonymous notification '''
        return dbsession.query(cls).filter_by(event_uuid=uuid).all()

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
        cls.__anonymous__(title, message, ERROR, event_uuid)
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
        dbsession.commit()

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
        return notification

    def to_dict(self):
        ''' Return public data as dict '''
        return {
            'uuid': self.uuid,
            'category': self.category,
            'title': self.title,
            'message': self.message,
            'icon_url': self.icon_url,
        }

