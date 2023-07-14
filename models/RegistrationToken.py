# -*- coding: utf-8 -*-
"""
Created on Sep 22, 2012

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


import binascii
from os import urandom
from sqlalchemy import Column
from sqlalchemy.types import String, Boolean
from models import dbsession
from models.BaseModels import DatabaseObject
from libs.StringCoding import encode, decode
from builtins import str


gen_token = lambda: binascii.hexlify(urandom(3))


class RegistrationToken(DatabaseObject):
    """Registration token definition"""

    value = Column(String(6), unique=True, nullable=False, default=gen_token)
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
    def count(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).count()

    @classmethod
    def by_value(cls, _value):
        """Returns a the object with value of value"""
        return dbsession.query(cls).filter_by(value=encode(_value)).first()
    
    def getvalue(self):
        return  decode(self.value)
    

