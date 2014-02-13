# -*- coding: utf-8 -*-
'''
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
'''


import os

from uuid import uuid4
from models import dbsession
from models.BaseModels import DatabaseObject
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.types import Unicode, String, Integer
from string import printable
from mimetypes import guess_type
from libs.ConfigManager import ConfigManager


class FileUpload(DatabaseObject):

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    byte_size = Column(Integer, nullable=False)
    _description = Column(Unicode(1024), nullable=False)
    _file_name = Column(Unicode(64), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_file_name(cls, file_name):
        ''' Return the user object whose file name is "file_name" '''
        return dbsession.query(cls).filter_by(_file_name=unicode(file_name)).first()

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = os.path.basename(value)

    @property
    def content_type(self):
        content = guess_type(self.file_name)
        return content[0] if content[0] is not None else 'unknown'

    @property
    def description(self):
        return self._description if self._description else u'No description'

    @description.setter
    def description(self, value):
        self._description = unicode(value)

    @property
    def data(self):
        config = ConfigManager.instance()
        with open(config.file_uploads_dir + self.uuid, 'rb') as fp:
            return fp.read().decode('base64')

    @data.setter
    def data(self, value):
        config = ConfigManager.instance()
        if self.uuid is None:
            self.uuid = str(uuid4())
        self.byte_size = len(value)
        with open(config.file_uploads_dir + self.uuid, 'wb') as fp:
            fp.write(value.encode('base64'))

    def delete_data(self):
        config = ConfigManager.instance()
        if os.path.exists(config.file_uploads_dir + self.uuid):
            os.unlink(config.file_uploads_dir + self.uuid)

    def __repr__(self):
        return u'<FileUpload - name: %s, size: %s>' % (self.file_name, self.byte_size)
