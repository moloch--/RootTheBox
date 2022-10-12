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

from sqlalchemy.types import Unicode, Integer
from sqlalchemy import Column, ForeignKey
from models import dbsession
from models.BaseModels import DatabaseObject


class Permission(DatabaseObject):
    """Permission definition"""

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(Unicode(64), nullable=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_user_id(cls, _id):
        return dbsession.query(cls).filter_by(user_id=_id).all()

    def to_xml(self, parent):
        pass

    def __repr__(self):
        return "<Permission - name: %s, user_id: %d>" % (self.name, self.user_id)
