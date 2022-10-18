# -*- coding: utf-8 -*-
"""
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
"""


from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, String
from models import dbsession
from models.BaseModels import DatabaseObject
from tornado.options import options
from builtins import str


class PasteBin(DatabaseObject):
    """PasteBin definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    _name = Column(Unicode(32), nullable=False)
    _contents = Column(Unicode(options.max_pastebin_size), nullable=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Get a paste object by uuid"""
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, value):
        self._contents = str(value[: options.max_pastebin_size])

    def __repr__(self):
        return "<PasteBin - name:%s, user_id:%d>" % (self.name, self.user_id)
