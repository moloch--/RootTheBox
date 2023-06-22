# -*- coding: utf-8 -*-
"""
Created on Jan 29, 2021

@author: eljeffe

    Copyright 2021 Root the Box

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
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import String, Boolean, Integer
from models import dbsession
from models.BaseModels import DatabaseObject
from libs.StringCoding import encode
from datetime import datetime, timedelta


class EmailToken(DatabaseObject):
    """Email verification token definition"""

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(64), unique=True, nullable=False)
    valid = Column(Boolean, nullable=False, default=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_user_id(cls, user_id, all=False):
        """Returns the object with id of user_id"""
        if all:
            return dbsession.query(cls).filter_by(user_id=user_id).all()
        else:
            return (
                dbsession.query(cls)
                .filter_by(user_id=user_id)
                .order_by(desc("id"))
                .first()
            )

    @classmethod
    def count(cls):
        """Returns a count of all objects in the database"""
        return dbsession.query(cls).count()

    @classmethod
    def by_value(cls, value):
        """Returns the object with value of value"""
        return dbsession.query(cls).filter_by(value=value).order_by(desc("id")).first()
