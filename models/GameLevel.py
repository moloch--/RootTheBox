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


from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer
from sqlalchemy.orm import relationship, backref
from models.Flag import Flag
from models.BaseGameObject import BaseObject


class GameLevel(BaseObject):
    ''' Game Level definition '''

    name = Column(Unicode(64), unique=True, nullable=False)
    number = Column(Integer, nullable=False)
    buyout = Column(Integer, nullable=False)
    banner_uri = Column(Unicode(255), nullable=False)
    flags = relationship("Flag", backref=backref(
        "GameLevel", lazy="joined"), cascade="all, delete-orphan")

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()