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


from uuid import uuid4
from sqlalchemy import Column, ForeignKey, asc
from sqlalchemy.types import Unicode, Integer, String
from sqlalchemy.orm import relationship, backref
from models import dbsession
from models.BaseGameObject import BaseObject


class GameLevel(BaseObject):
    ''' Game Level definition '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: uuid4())
    number = Column(Integer, unique=True, nullable=False)
    next_level_id = Column(Integer, ForeignKey('game_level.id'))
    buyout = Column(Integer, nullable=False)
    boxes = relationship("Box", backref=backref("GameLevel", lazy="joined"), cascade="all, delete-orphan")

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).order_by(asc(cls.number)).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_number(cls, number):
        ''' Returns a the object with number of number '''
        return dbsession.query(cls).filter_by(number=number).first()

    @property
    def flags(self):
        ''' Return all flags for the level '''
        flags = []
        for box in self.boxes:
            for flag in box.flags:
                flags.append(flag)
        return flags

    def next(self):
        ''' Return the next level, or None '''
        if self.next_level_id is not None:
            return self.by_id(self.next_level_id)
        else:
            return None

    def to_dict(self):
        return dict(
            uuid=self.uuid,
            number=self.number,
            buyout=self.buyout,
        )

    def __str__(self):
        return str(self.number)

    def __cmp__(self, other):
        if self.number < other.number:
            return -1
        else:
            return 1