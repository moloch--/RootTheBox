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


import re
import hashlib
import xml.etree.cElementTree as ET

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Boolean, String
from models import dbsession, Box
from models.BaseGameObject import BaseObject


### Constants
FLAG_STATIC = u'static'
FLAG_REGEX  = u'regex'
FLAG_FILE   = u'file'


class Flag(BaseObject):
    ''' Flag definition '''

    name = Column(Unicode(32), nullable=False)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    token = Column(Unicode(256), nullable=False)
    description = Column(Unicode(256), nullable=False)
    value = Column(Integer, nullable=False)
    _type = Column(Unicode(16), default=False)
    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)
    FLAG_TYPES = [FLAG_FILE, FLAG_REGEX, FLAG_STATIC]

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_name(cls, fname):
        ''' Returns a the object with name of fname '''
        return dbsession.query(cls).filter_by(name=unicode(fname)).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_token(cls, token):
        ''' Return and object based on a token '''
        return dbsession.query(cls).filter_by(token=unicode(token)).first()

    @classmethod
    def by_type(cls, _type):
        ''' Return and object based on a token '''
        return dbsession.query(cls).filter_by(_type=unicode(_type)).all()

    @classmethod
    def create_flag(cls, _type, box, name, raw_token, description, value):
        ''' Check parameters applicable to all flag types '''
        creators = {
            FLAG_STATIC: cls._create_flag_static,
             FLAG_REGEX: cls._create_flag_regex,
              FLAG_FILE: cls._create_flag_file,
        }
        name = unicode(name)
        description = unicode(description)
        if cls.by_name(name) is not None:
            raise ValueError('Flag name already exists in database')
        if not isinstance(value, int):
            raise ValueError('Flag value must be an integer')
        if not isinstance(description, basestring) or not len(description):
            raise ValueError('Flag description is not valid')
        assert box is not None and isinstance(box, Box)
        new_flag = creators[_type](box, name, raw_token, description, value)
        new_flag._type = _type
        return new_flag

    @classmethod
    def _create_flag_file(cls, box,  name, raw_token, description, value):
        ''' Check flag file specific parameters '''
        token = cls.digest(raw_token)
        if cls.by_token(token) is not None:
            raise ValueError('Flag token already exists in database')
        return cls(box_id=box.id, name=name, token=token, description=description, value=value)

    @classmethod
    def _create_flag_regex(cls, box,  name, raw_token, description, value):
        ''' Check flag regex specific parameters '''
        token = unicode(raw_token)
        try:
            re.compile(token)
        except:
            raise ValueError('Flag token is not a valid regex')
        if cls.by_token(token) is not None:
            raise ValueError('Flag token already exists in database')
        return cls(box_id=box.id, name=name, token=token, description=description, value=value)

    @classmethod
    def _create_flag_static(cls, box,  name, raw_token, description, value):
        ''' Check flag static specific parameters '''
        token = unicode(raw_token)
        if cls.by_token(raw_token) is not None:
            raise ValueError('Flag token already exists in database')
        return cls(box_id=box.id, name=name, token=raw_token, description=description, value=value)

    @classmethod
    def digest(self, data):
        ''' Token is SHA1 of data '''
        sha = hashlib.sha1()
        sha.update(data)
        return unicode(sha.hexdigest())

    @property
    def box(self):
        return Box.by_id(self.box_id)

    @property
    def game_level(self):
        return self.box.game_level

    @property
    def is_file(self):
        return self._type == FLAG_FILE

    def capture(self, submission):
        if self._type == FLAG_STATIC:
            return self.token == submission
        elif self._type == FLAG_REGEX:
            pattern = re.compile(self.token)
            return pattern.match(submission) is not None
        elif self._type == FLAG_FILE:
            self.token == self.digest(submission)
        else:
            raise ValueError('Invalid flag type, cannot capture')

    def to_xml(self, parent):
        ''' Write attributes to XML doc '''
        flag_elem = ET.SubElement(parent, "flag")
        flag_elem.set("type", str(self._type))
        ET.SubElement(flag_elem, "name").text = str(self.name)
        ET.SubElement(flag_elem, "token").text = str(self.token)
        ET.SubElement(flag_elem, "description").text = str(self.description)
        ET.SubElement(flag_elem, "value").text = str(self.value)

    def to_dict(self):
        ''' Returns public data as a dict '''
        box = Box.by_id(self.box_id)
        return {
            'name': self.name,
            'uuid': self.uuid,
            'description': self.description,
            'value': self.value,
            'box': box.uuid,
            'token': self.token,
        }

    def __str__(self):
        return self.name.encode('ascii', 'ignore')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<Flag - name:%s, type:%s >" % (
            self.name, str(self._type)
        )