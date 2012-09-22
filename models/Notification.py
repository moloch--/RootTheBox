# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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


import os
import json
import imghdr

from urlparse import urlparse
from libs.Memcache import FileCache
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession
from models.BaseGameObject import BaseObject


class Notification(BaseObject):
    ''' Notification definition '''

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(Unicode(255), nullable=False)
    message = Column(Unicode(255), nullable=False)
    viewed = Column(Boolean, default=False)
    icon_url = Column(Unicode(255), nullable=True)
    category = Column(Unicode(64), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_user_id(cls, user_id):
        ''' Return notifications for a single user '''
        return dbsession.query(cls).filter_by(user_id=user_id).order_by(desc(cls.created)).all()

    @classmethod
    def new_messages(cls, user_id):
        ''' Return all notification which have not been viewed '''
        ls = cls.by_user_id(user_id)
        return filter(lambda note: note.viewed == False, ls)

    def to_json(self):
        ''' Creates a JSON version of the notification '''
        notification = {
            'category': self.category,
            'title': self.title,
            'message': self.message,
            'icon_url': self.icon_url,
        }
        return json.dumps(notification)
