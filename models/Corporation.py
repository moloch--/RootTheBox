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
from sqlalchemy import Column
from sqlalchemy.types import Unicode, String
from sqlalchemy.orm import relationship, backref
from libs.ValidationError import ValidationError
from builtins import str
from models import dbsession
from models.BaseModels import DatabaseObject


class Corporation(DatabaseObject):
    """ Corporation definition """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    _name = Column(Unicode(32), unique=True, nullable=False)

    boxes = relationship(
        "Box",
        backref=backref("corporation", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    @classmethod
    def all(cls):
        """ Returns a list of all objects in the database """
        return dbsession.query(cls).all()

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @classmethod
    def by_id(cls, _id):
        """ Returns a the object with id of _id """
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, name):
        """ Returns a the object with name of name """
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def by_uuid(cls, uuid):
        """ Return an object based on uuid """
        return dbsession.query(cls).filter_by(uuid=uuid).first()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not len(value) <= 32:
            raise ValidationError("Corporation name must be 0 - 32 characters")
        self._name = str(value)

    def to_dict(self):
        """ Returns editable data as a dictionary """
        return {
            "uuid": self.uuid,
            "name": self.name,
            # "boxes": [box.uuid for box in self.boxes],
        }

    def to_xml(self, parent):
        """ Add to XML dom """
        corp_elem = ET.SubElement(parent, "corporation")
        ET.SubElement(corp_elem, "name").text = self.name
        boxes_elem = ET.SubElement(corp_elem, "boxes")
        boxes_elem.set("count", str(len(self.boxes)))
        for box in self.boxes:
            box.to_xml(boxes_elem)

    def __len__(self):
        return len(self.boxes)

    def __str__(self):
        return self.name
