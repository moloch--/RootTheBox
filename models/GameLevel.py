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


import xml.etree.cElementTree as ET

from uuid import uuid4
from sqlalchemy import Column, ForeignKey, asc
from sqlalchemy.types import Unicode, Integer, String, Boolean
from sqlalchemy.orm import relationship, backref
from libs.ValidationError import ValidationError
from models import dbsession
from models.BaseModels import DatabaseObject
from builtins import str
from models.Relationships import team_to_game_level


class GameLevel(DatabaseObject):

    """Game Level definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    next_level_id = Column(Integer, ForeignKey("game_level.id"))
    _number = Column(Integer, unique=True, nullable=False)
    _buyout = Column(Integer, nullable=False)
    _type = Column(Unicode(16), nullable=False, default=str("none"))
    _reward = Column(Integer, nullable=False, default=0)
    _name = Column(Unicode(32), nullable=True)
    _description = Column(Unicode(512))
    _locked = Column(Boolean, default=False, nullable=False)

    boxes = relationship(
        "Box",
        backref=backref("game_level", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    teams = relationship(
        "Team",
        secondary=team_to_game_level,
        back_populates="game_levels",
        lazy="select",
    )

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).order_by(asc(cls._number)).all()

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a _uuid"""
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_number(cls, number):
        """Returns a the object with number of number"""
        return dbsession.query(cls).filter_by(_number=abs(int(number))).first()

    @classmethod
    def last_level(cls, number):
        """Returns the prior level"""
        return dbsession.query(cls).filter_by(next_level_id=int(number)).first()

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        try:
            if self.by_number(value) is None:
                self._number = abs(int(value))
            elif self.uuid != self.by_number(value).uuid:
                raise ValidationError("Game level number must be unique")
        except ValueError:
            raise ValidationError("Game level number must be an integer")

    @property
    def buyout(self):
        if self._buyout is None:
            return 0
        return self._buyout

    @buyout.setter
    def buyout(self, value):
        try:
            self._buyout = abs(int(value))
        except ValueError:
            raise ValidationError("Buyout value must be an integer")

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, value):
        try:
            self._reward = abs(int(value))
        except ValueError:
            raise ValidationError("Reward value must be an integer")

    @property
    def name(self):
        if self._name:
            return str(self._name)
        else:
            return "Level #" + str(self.number)

    @name.setter
    def name(self, value):
        if len(value) <= 32:
            self._name = value
        else:
            raise ValidationError("Max name length is 32")

    @property
    def description(self):
        if self._description is None:
            return ""
        return self._description

    @description.setter
    def description(self, value):
        if 512 < len(value):
            raise ValidationError("Description cannot be greater than 512 characters")
        self._description = str(value)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value is None:
            return
        try:
            self._type = str(value)
        except ValueError:
            raise ValidationError("type value must be an string")

    @property
    def flags(self):
        """Return all flags for the level"""
        _flags = []
        for box in self.boxes:
            _flags += sorted(box.flags)
        return _flags

    @property
    def locked(self):
        """Determines if an admin has locked an level."""
        if self._locked == None:
            return False
        return self._locked

    @locked.setter
    def locked(self, value):
        """Setter method for _lock"""
        if value is None:
            value = False
        elif isinstance(value, int):
            value = value == 1
        elif isinstance(value, str):
            value = value.lower() in ["true", "1"]
        assert isinstance(value, bool)
        self._locked = value

    def unlocked_boxes(self):
        if self._locked:
            return []
        return [box for box in self.boxes if not box.locked]

    def to_xml(self, parent):
        level_elem = ET.SubElement(parent, "gamelevel")
        ET.SubElement(level_elem, "number").text = str(self.number)
        ET.SubElement(level_elem, "buyout").text = str(self.buyout)
        ET.SubElement(level_elem, "type").text = str(self._type)
        ET.SubElement(level_elem, "reward").text = str(self._reward)
        ET.SubElement(level_elem, "name").text = str(self._name)
        ET.SubElement(level_elem, "description").text = str(self._description)
        ET.SubElement(level_elem, "locked").text = str(self.locked)

    def to_dict(self):
        """Return public data as dict"""
        last = GameLevel.last_level(self.id)
        if last:
            last_level = last.number
        else:
            last_level = ""
        return {
            "uuid": self.uuid,
            "number": self.number,
            "name": self.name,
            "buyout": self.buyout,
            "type": self.type,
            "reward": self.reward,
            "description": self.description,
            "last_level": last_level,
        }

    def __next__(self):
        """Return the next level, or None"""
        if self.next_level_id is not None:
            return self.by_id(self.next_level_id)
        else:
            return None

    def __str__(self):
        return "GameLevel #%d" % self.number

    def __cmp__(self, other):
        if self.number < other.number:
            return -1
        else:
            return 1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __repr__(self):
        return "<GameLevel number: %d, buyout: %d, next: id(%s)>" % (
            self.number,
            self.buyout,
            self.next_level_id,
        )

    def __hash__(self):
        return hash(self.uuid)
