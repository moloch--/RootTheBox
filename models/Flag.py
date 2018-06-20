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
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Unicode, Integer, String
from models import dbsession
from models.Box import Box
from models.FlagAttachment import FlagAttachment  # Fix object mapper
from models.BaseModels import DatabaseObject
from libs.ValidationError import ValidationError
from tornado.options import options

### Constants
FLAG_STATIC = u'static'
FLAG_REGEX = u'regex'
FLAG_FILE = u'file'
FLAG_DATETIME = u'datetime'


class Flag(DatabaseObject):

    '''
    Flags that can be captured by players and what not. This object comes in
    these flavors:
        -static
        -regex
        -datetime
        -file

    Depending on the cls._type value. For more information see the wiki.
    '''

    uuid = Column(String(36),
                  unique=True,
                  nullable=False,
                  default=lambda: str(uuid4())
                  )
    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)
    lock_id = Column(Integer, ForeignKey('flag.id', ondelete="SET NULL"), nullable=True)

    _name = Column(Unicode(64), nullable=False)
    _token = Column(Unicode(256), nullable=False)
    _description = Column(Unicode(1024), nullable=False)
    _capture_message = Column(Unicode(512))
    _case_sensitive = Column(Integer, nullable=True)
    _value = Column(Integer, nullable=False)
    _type = Column(Unicode(16), default=False)

    flag_attachments = relationship("FlagAttachment",
                                    backref=backref("flag", lazy="select")
                                    )

    FLAG_TYPES = [FLAG_FILE, FLAG_REGEX, FLAG_STATIC, FLAG_DATETIME]

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, name):
        ''' Returns a the object with name of _name '''
        return dbsession.query(cls).filter_by(_name=unicode(name)).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(_uuid)).first()

    @classmethod
    def by_token(cls, token):
        ''' Return and object based on a token '''
        return dbsession.query(cls).filter_by(_token=unicode(token)).first()

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
            FLAG_DATETIME: cls._create_flag_datetime,
        }
        #TODO Don't understand why this is here - name is not unqiue value
        # and you could simply name questions per box, like "Question 1" - ElJefe 6/1/2018
        #if cls.by_name(name) is not None:
            #raise ValidationError('Flag name already exists in database')
        assert box is not None and isinstance(box, Box)
        new_flag = creators[_type](box, name, raw_token, description, value)
        new_flag._type = _type
        return new_flag

    @classmethod
    def _create_flag_file(cls, box,  name, raw_token, description, value):
        ''' Check flag file specific parameters '''
        token = cls.digest(raw_token)
        if not options.debug and cls.by_token(token) is not None:
            raise ValidationError('Flag token already exists in database')
        return cls(box_id=box.id,
                   name=name,
                   token=token,
                   description=description,
                   value=value
                   )

    @classmethod
    def _create_flag_regex(cls, box,  name, raw_token, description, value):
        ''' Check flag regex specific parameters '''
        try:
            re.compile(raw_token)
        except:
            raise ValidationError('Flag token is not a valid regex')
        if not options.debug and cls.by_token(raw_token) is not None:
            raise ValidationError('Flag token already exists in database')
        return cls(box_id=box.id,
                   name=name,
                   token=raw_token,
                   description=description,
                   value=value
                   )

    @classmethod
    def _create_flag_static(cls, box,  name, raw_token, description, value):
        ''' Check flag static specific parameters '''
        if not options.debug and cls.by_token(raw_token) is not None:
            raise ValidationError('Flag token already exists in database')
        return cls(box_id=box.id,
                   name=name,
                   token=raw_token,
                   description=description,
                   value=value
                   )

    @classmethod
    def _create_flag_datetime(cls, box,  name, raw_token, description, value):
        ''' Check flag datetime specific parameters '''
        if cls.by_token(raw_token) is not None:
            raise ValidationError('Flag token already exists in database')
        return cls(box_id=box.id,
                   name=name,
                   token=raw_token,
                   description=description,
                   value=value
                   )

    @classmethod
    def digest(self, data):
        ''' Token is SHA1 of data '''
        return hashlib.sha1(data).hexdigest()

    @property
    def game_level(self):
        return self.box.game_level

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not 3 <= len(value) <= 16:
            raise ValidationError("Flag name must be 3 - 16 characters")
        #TODO Perhaps same name with the same box - ElJefe 6/1/2018
        #if self.by_name(value) is not None:
            #raise ValidationError("Flag name must be unique")
        self._name = unicode(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = unicode(value)[:256]

    @property
    def capture_message(self):
        return self._capture_message if self._capture_message else ''

    @capture_message.setter
    def capture_message(self, value):
        self._capture_message = unicode(value)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in self.FLAG_TYPES:
            raise ValueError("Invalid flag type")
        self._type = unicode(value)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = unicode(value)

    @property
    def case_sensitive(self):
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value):
        self._case_sensitive = unicode(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = abs(int(value))
        except ValueError:
            raise ValidationError("Reward value must be an integer")

    @property
    def is_file(self):
        return self._type == FLAG_FILE

    def capture(self, submission):
        if self._type == FLAG_STATIC:
            if self._case_sensitive == 0:
                return str(self.token).lower().strip() == str(submission).lower().strip()
            else:
                return str(self.token).strip() == str(submission).strip()
        elif self._type == FLAG_REGEX:
            if not self.token.startswith("^(") and not self.token.endswith(")$"):
                self.token = "^(" + self.token + ")$"
            if self._case_sensitive == 0:
                pattern = re.compile(self.token, re.IGNORECASE)
            else:
                pattern = re.compile(self.token)
            return pattern.match(submission) is not None
        elif self._type == FLAG_FILE:
            return self.token == self.digest(submission)
        elif self._type == FLAG_DATETIME:
            from dateutil.parser import parse
            try:
                return parse(self.token) == parse(submission)
            except:
                return False
        else:
            raise ValueError('Invalid flag type, cannot capture')

    def to_xml(self, parent):
        ''' Write attributes to XML doc '''
        flag_elem = ET.SubElement(parent, "flag")
        flag_elem.set("type", self._type)
        ET.SubElement(flag_elem, "name").text = self.name
        ET.SubElement(flag_elem, "token").text = self.token
        ET.SubElement(flag_elem, "description").text = self.description
        ET.SubElement(flag_elem, "capture_message").text = self.capture_message
        ET.SubElement(flag_elem, "value").text = str(self.value)
        ET.SubElement(flag_elem, "case_sensitive").text = self.case_sensitive
        attachements_elem = ET.SubElement(flag_elem, "flag_attachments")
        attachements_elem.set("count", str(len(self.flag_attachments)))
        for attachement in self.flag_attachments:
            attachement.to_xml(attachements_elem)

    def to_dict(self):
        ''' Returns public data as a dict '''
        box = Box.by_id(self.box_id)
        if self.lock_id:
            lock_uuid = Flag.by_id(self.lock_id).uuid
        else:
            lock_uuid = ''
        case_sensitive = self.case_sensitive
        if case_sensitive != 0:
            case_sensitive = 1
        return {
            'name': self.name,
            'uuid': self.uuid,
            'description': self.description,
            'capture_message': self.capture_message,
            'value': self.value,
            'box': box.uuid,
            'token': self.token,
            'lock_uuid': lock_uuid,
            'case-sensitive': case_sensitive,
            'flagtype': self.type
        }

    def __repr__(self):
        return "<Flag - name:%s, type:%s >" % (
            self.name, str(self._type)
        )
