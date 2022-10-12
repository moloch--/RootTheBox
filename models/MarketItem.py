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


import json

from uuid import uuid4
from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer, String
from models.BaseModels import DatabaseObject
from models import dbsession
from builtins import str


class MarketItem(DatabaseObject):
    """Item definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    name = Column(Unicode(64), nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(Unicode(256), nullable=False)
    description = Column(Unicode(1024))

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
        """Returns a the object with a given uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def by_name(cls, _name):
        """Returns an object with a given name"""
        return dbsession.query(cls).filter_by(name=str(_name)).first()

    def to_dict(self):
        """Returns object data as dictionary object"""
        return {
            "name": self.name,
            "price": self.price,
            "image": self.image,
            "description": self.description,
            "uuid": self.uuid,
        }

    def __eq__(self, other):
        """Equivalency"""
        return self.uuid == other.uuid

    def __ne__(self, other):
        """Not Equivalent"""
        return not self == other

    def __hash__(self):
        return hash(self.name)
