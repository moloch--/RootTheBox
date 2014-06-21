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

import os

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Boolean, String
from models.BaseModels import DatabaseObject
from mimetypes import guess_type
from libs.ConfigManager import ConfigManager


class FlagAttachment(DatabaseObject):
    ''' Flag definition '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    _file_name = Column(Unicode(64), nullable=False)
    byte_size = Column(Integer, nullable=False)

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = os.path.basename(value).replace('\n', '').replace('\r', '')

    @property
    def content_type(self):
        content = guess_type(self.file_name)
        return content[0] if content[0] is not None else 'unknown'

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

    def to_xml(self, parent):
        ''' XML Serialize '''
        attachment_elem = ET.SubElement(parent, "attachment")
        attachment_elem.set("byte_size", str(self.byte_size))
        ET.SubElement(attachment_elem, "name").text = self.name
        ET.SubElement(attachment_elem, "content_type").text = self.content_type
        config = ConfigManager.instance()
        with open(config.file_uploads_dir + self.uuid, 'rb') as fp:
            ET.SubElement(attachment_elem, "data").text = fp.read()