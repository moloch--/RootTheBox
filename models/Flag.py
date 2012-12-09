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

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession, Box
from models.BaseGameObject import BaseObject


class Flag(BaseObject):
    ''' Flag definition '''

    name = Column(Unicode(255), nullable=False)
    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    token = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255), nullable=False)
    value = Column(Integer, nullable=False)
    is_file = Column(Boolean, default=False)
    is_hash = Column(Boolean, default=False)
    is_regex = Column(Boolean, default=False)
    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_name(cls, corp_name):
        ''' Returns a the object with name of corp_name '''
        return dbsession.query(cls).filter_by(name=unicode(corp_name)).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_token(cls, token):
        ''' Return and object based on a token '''
        return dbsession.query(cls).filter_by(token=unicode(token)).first()

    @property
    def box(self):
        return Box.by_id(self.box_id)

    @property
    def game_level(self):
        return self.box.game_level

    def to_dict(self):
        ''' Returns editable data as a dictionary '''
        box = Box.by_id(self.box_id)
        return dict(
            name=self.name,
            uuid=self.uuid,
            token=self.token,
            description=self.description,
            value=self.value,
            box=box.uuid,
        )

    def __hsh__(self, data):
        ''' Token is MD5 of data '''
        md = hashlib.md5()
        md.update(data)
        return unicode(md.hexdigest())

    def __regex__(self, other):
        ''' Token is regex matched against other '''
        regex = re.compile(self.token)
        return bool(regex.match(other))

    def __str__(self):
        return self.name.encode('ascii', 'ignore')

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        ''' Compare to self.token '''
        if not isinstance(other, basestring):
            return str(self) == str(other)
        if self.is_hash or self.is_file:
            return self.token == self.__hsh__(other)
        elif self.is_regex:
            return self.__regex__(other)
        else:
            return self.token == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<Flag - name:%s, is_file:%s, is_hash:%s, is_regex:%s>" % \
            (self.name, str(self.is_file), str(self.is_hash), str(self.is_regex),)
