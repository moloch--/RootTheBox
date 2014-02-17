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
from libs.Memcache import FileCache
from libs.SecurityDecorators import debug
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.sql import and_
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession
from models.BaseModels import DatabaseObject


class Notification(DatabaseObject):
    ''' Notification definition '''

    user_id = Column(Integer, ForeignKey('user.id'))
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
        return dbsession.query(cls).filter_by(event_uuid=uuid).filter_by(user_id=None).first()

    @classmethod
    def delivered(cls, user_id, uuid):
        notify = dbsession.query(cls).filter(
            and_(cls.event_uuid == uuid, cls.user_id == user_id)
        ).first()
        notify.viewed = True
        dbsession.add(notify)
        dbsession.commit()

    def to_dict(self):
        ''' Return public data as dict '''
        return {
            'category': self.category,
            'title': self.title,
            'message': self.message,
            'icon_url': self.icon_url,
        }

