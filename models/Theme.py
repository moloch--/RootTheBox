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

import logging


from uuid import uuid4
from string import ascii_letters, digits
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship
from sqlalchemy.types import Unicode, Integer, Boolean, String
from models import dbsession
from models.BaseModels import DatabaseObject
from builtins import str
from tornado.options import options


class ThemeFile(DatabaseObject):
    """
    Holds theme related settings
    """

    theme_id = Column(Integer, ForeignKey("theme.id"), nullable=False)
    _file_name = Column(Unicode(64), nullable=False)

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        """Remove any non-white listed chars from a string"""
        char_white_list = ascii_letters + digits + extra_chars
        return "".join([char for char in string if char in char_white_list])

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = self._filter_string(value, ".")

    def endswith(self, needle):
        return str(self).endswith(needle)

    def __str__(self):
        return self._file_name

    def __unicode__(self):
        return self._file_name


class Theme(DatabaseObject):
    """
    Holds theme related settings
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    _name = Column(Unicode(64), unique=True, nullable=False)
    files = relationship("ThemeFile", lazy="joined")

    @classmethod
    def all(cls):
        """Return all objects"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Return the object whose id is _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return the object whose uuid is _uuid"""
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_name(cls, name):
        """Return the object whose name is _name"""
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        """Remove any non-white listed chars from a string"""
        char_white_list = ascii_letters + digits + extra_chars
        return "".join([char for char in string if char in char_white_list])

    @property
    def name(self):
        try:
            return self._name
        except:
            return options.default_theme

    @name.setter
    def name(self, value):
        self._name = self._filter_string(value, ".")

    def __iter__(self):
        try:
            for _file in self.files:
                yield _file
        except:
            logging.error(
                "Session Expired - returning default theme: %s" % options.default_theme
            )
            if self.name == "386":
                yield "386.js"
            else:
                yield "%s.min.css" % self.name.lower()
