# -*- coding: utf-8 -*-
"""
Created on Nov 24, 2014

@author: moloch

    Copyright 2014 Root the Box

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
import xml.etree.cElementTree as ET

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, String, Integer
from models.BaseModels import DatabaseObject
from libs.StringCoding import encode, decode
from builtins import str
from tornado.options import options


class FlagAttachment(DatabaseObject):

    """
    These are files that the administrator wants to
    distribute alongside a flag.
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    flag_id = Column(Integer, ForeignKey("flag.id"), nullable=False)
    _file_name = Column(Unicode(64), nullable=False)

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        fname = value.replace("\n", "").replace("\r", "")
        self._file_name = str(os.path.basename(fname))[:64]

    @property
    def data(self):
        with open(options.flag_attachment_dir + "/" + self.uuid, "rb") as fp:
            return decode(fp.read(), "base64")

    @data.setter
    def data(self, value):
        if self.uuid is None:
            self.uuid = str(uuid4())
        self.byte_size = len(value)
        with open(options.flag_attachment_dir + "/" + self.uuid, "wb") as fp:
            fp.write(str(encode(value, "base64")).encode())

    def delete_data(self):
        """Remove the file from the file system, if it exists"""
        fpath = options.flag_attachment_dir + "/" + self.uuid
        if os.path.exists(fpath) and os.path.isfile(fpath):
            os.unlink(fpath)

    def to_xml(self, parent):
        attachment_elem = ET.SubElement(parent, "flag_attachment")
        ET.SubElement(attachment_elem, "file_name").text = self.file_name
        with open(options.flag_attachment_dir + "/" + self.uuid, mode="rb") as fp:
            data = fp.read()
            ET.SubElement(attachment_elem, "data").text = encode(data, "base64")

    def to_dict(self):
        return {"file_name": self.file_name, "data": self.data}
