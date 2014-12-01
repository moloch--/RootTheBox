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


import xml.etree.cElementTree as ET

from uuid import uuid4
from sqlalchemy import Column, ForeignKey, asc
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relationship, backref
from libs.ValidationError import ValidationError
from models import dbsession
from models.BaseModels import DatabaseObject


class GameLevel(DatabaseObject):

    ''' Game Level definition '''

    uuid = Column(String(36),
                  unique=True,
                  nullable=False,
                  default=lambda: str(uuid4())
                  )

    next_level_id = Column(Integer, ForeignKey('game_level.id'))
    _number = Column(Integer, unique=True, nullable=False)
    _buyout = Column(Integer, nullable=False)

    boxes = relationship("Box",
                         backref=backref("game_level", lazy="select"),
                         cascade="all,delete,delete-orphan"
                         )

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).order_by(asc(cls._number)).all()

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Return and object based on a _uuid '''
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_number(cls, number):
        ''' Returns a the object with number of number '''
        return dbsession.query(cls).filter_by(_number=abs(int(number))).first()

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        try:
            if self.by_number(value) is None:
                self._number = abs(int(value))
            else:
                raise ValidationError("Game level number must be unique")
        except ValueError:
            raise ValidationError("Game level number must be an integer")

    @property
    def buyout(self):
        return self._buyout

    @buyout.setter
    def buyout(self, value):
        try:
            self._buyout = abs(int(value))
        except ValueError:
            raise ValidationError("Buyout value must be an integer")

    @property
    def flags(self):
        ''' Return all flags for the level '''
        _flags = []
        for box in self.boxes:
            _flags += box.flags
        return _flags

    def next(self):
        ''' Return the next level, or None '''
        if self.next_level_id is not None:
            return self.by_id(self.next_level_id)
        else:
            return None

    def to_xml(self, parent):
        level_elem = ET.SubElement(parent, "gamelevel")
        ET.SubElement(level_elem, "number").text = str(self.number)
        ET.SubElement(level_elem, "buyout").text = str(self.buyout)

    def to_dict(self):
        ''' Return public data as dict '''
        return {
            'uuid': self.uuid,
            'number': self.number,
            'buyout': self.buyout,
        }

    def __str__(self):
        return "GameLevel #%d" % self.number

    def __cmp__(self, other):
        if self.number < other.number:
            return -1
        else:
            return 1

    def __repr__(self):
        return "<GameLevel number: %d, buyout: %d, next: id(%s)>" % (
            self.number, self.buyout, self.next_level_id
        )
