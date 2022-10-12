# -*- coding: utf-8 -*-
"""
Created on Sep 6, 2020

@author: eljeffe

    Copyright 2020 Root the Box

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


from os import urandom
from hashlib import sha256
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import String, Boolean, Integer
from models import dbsession
from models.BaseModels import DatabaseObject
from libs.StringCoding import encode
from datetime import datetime, timedelta


class PasswordToken(DatabaseObject):
    """Password token definition"""

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(64), unique=True, nullable=False)
    used = Column(Boolean, nullable=False, default=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_user_id(cls, user_id):
        """Returns a the object with id of user_id"""
        return dbsession.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    def count(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).count()

    @classmethod
    def by_value(cls, value):
        """Returns a the object with value of value"""
        return dbsession.query(cls).filter_by(value=value).first()

    def is_expired(self, hours=3):
        """Check if the token is expired"""
        now = datetime.now()
        expired = self.created + timedelta(hours=hours)
        return now > expired
