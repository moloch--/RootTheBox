# -*- coding: utf-8 -*-
"""
Created on Mar 15, 2012

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


import os

from uuid import uuid4
from models import dbsession
from models.BaseModels import DatabaseObject
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, String, Integer
from mimetypes import guess_type
from tornado.options import options
from string import printable
from libs.ValidationError import ValidationError
from libs.StringCoding import encode, decode
from builtins import str


MAX_FILE_SIZE = 50 * (1024**2)  # Max file size 50Mb


class FileUpload(DatabaseObject):

    """
    This is the object that stores data about files shared by
    players via the team file sharing feature.
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    byte_size = Column(Integer, nullable=False)
    _description = Column(Unicode(1024), nullable=False)
    _file_name = Column(Unicode(64), nullable=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        fname = str(os.path.basename(value))[:64]
        fname = "".join([char for char in fname if char in printable[:-6]])
        if len(fname) <= 2:
            raise ValidationError("File name is too short")
        self._file_name = fname

    @property
    def content_type(self):
        content = guess_type(self.file_name)
        if content[0] is not None:
            return content[0]
        else:
            "application/octet-stream"

    @property
    def description(self):
        return self._description if self._description else "No description"

    @description.setter
    def description(self, value):
        self._description = str(value)

    @property
    def data(self):
        with open(options.share_dir + "/" + self.uuid, "rb") as fp:
            return decode(fp.read(), "base64")

    @data.setter
    def data(self, value):
        if MAX_FILE_SIZE <= len(value):
            raise ValidationError("File is too large")
        if self.uuid is None:
            self.uuid = str(uuid4())
        self.byte_size = len(value)
        with open(options.share_dir + "/" + self.uuid, "wb") as fp:
            fp.write(str(encode(value, "base64")).encode())

    def delete_data(self):
        if os.path.exists(options.share_dir + "/" + self.uuid):
            os.unlink(options.share_dir + "/" + self.uuid)

    def __repr__(self):
        return "<FileUpload - name: %s, size: %s>" % (self.file_name, self.byte_size)
