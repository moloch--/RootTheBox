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

from libs.Memcache import FileCache
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Boolean
from models.BaseGameObject import BaseObject


class Notification(BaseObject):
    ''' Notification definition '''

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(Unicode(255), nullable=False)
    message = Column(Unicode(255), nullable=False)
    viewed = Column(Boolean, default=False)
    _icon = Column(Unicode(255))

    @classmethod
    def by_id(cls, notify_id):
        ''' Return the notification object whose notification id is "notify_id" '''
        return dbsession.query(cls).filter_by(id=notify_id).first()

    @property
    def icon():
        ''' Gets icon data from disk or cache '''
        return FileCache.get(self._icon)

    @icon.setter
    def icon(self, file_path):
        ''' Sets path to icon file '''
        if os.path.exists(file_path):
            self._icon = file_path
        else:
            raise ValueError

    def to_json(self):
        ''' Creates a JSON version of the notification '''
        notification = {
            title: self.title,
            message: self.message,
            icon: self.icon
        }
        return json.dumps(notification)

    def __cmp__(self, other):
        ''' Compares data/time the notification was created '''
        if self.created < other:
            return -1
        elif self.created == other:
            return 0
        else:
            return 1
