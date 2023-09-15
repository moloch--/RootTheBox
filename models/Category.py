# -*- coding: utf-8 -*-
"""
Created on Jun 19, 2018

@author: eljefe

    Copyright 2018 Root the Box

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
import json

from uuid import uuid4
from sqlalchemy import Column
from sqlalchemy.types import Unicode, String
from sqlalchemy.orm import relationship, backref
from libs.ValidationError import ValidationError
from builtins import str
from models import dbsession
from models.BaseModels import DatabaseObject


class Category(DatabaseObject):
    """Category definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    _category = Column(Unicode(64), unique=True, nullable=False)
    _description = Column(Unicode(4096), nullable=True)

    boxes = relationship("Box", backref=backref("category", lazy="select"))

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def list(cls):
        """Returns a list of all categories in the database"""
        categories = dbsession.query(cls).all()
        catlist = []
        for cat in categories:
            catlist.append(cat.category)
        return json.dumps(catlist)

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_category(cls, name):
        """Returns a the object with category of name"""
        return dbsession.query(cls).filter_by(_category=str(name)).first()

    @classmethod
    def by_uuid(cls, uuid):
        """Return an object based on uuid"""
        return dbsession.query(cls).filter_by(uuid=uuid).first()

    @property
    def description(self):
        if self._description is None:
            return ""
        return self._description

    @description.setter
    def description(self, value):
        if 4096 < len(value):
            raise ValidationError("Description cannot be greater than 4096 characters")
        self._description = str(value)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not len(value) <= 64:
            raise ValidationError("Category name must be 0 - 64 characters")
        self._category = str(value)

    def to_dict(self):
        """Returns editable data as a dictionary"""
        return {
            "uuid": self.uuid,
            "category": self.category,
            "description": self.description,
        }

    def to_xml(self, parent):
        """Add to XML dom"""
        cat_elem = ET.SubElement(parent, "category")
        ET.SubElement(cat_elem, "category").text = self.category
        ET.SubElement(cat_elem, "description").text = self.description

    def __len__(self):
        return len(self.boxes)

    def __str__(self):
        return self.category
