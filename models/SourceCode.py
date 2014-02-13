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


from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.types import String, Unicode, Integer, String
from models import dbsession
from models.BaseModels import DatabaseObject
from string import ascii_letters, digits


class SourceCode(DatabaseObject):
    '''
    Holds the source code for a box which can be purchased from the source code market
    '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)
    _price = Column(Integer, nullable=False)
    _description = Column(Unicode(1024), nullable=False)
    checksum = Column(String(40))

    _file_name = Column(String(64), nullable=False)
    file_name = synonym('_file_name', descriptor=property(
        lambda self: self._file_name,
        lambda self, file_name: setattr(
            self, '_file_name', self.__class__.filter_string(file_name, ".-_"))
    ))

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
        ''' Returns a the object with a given _uuid '''
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_box_id(cls, _id):
        return dbsession.query(cls).filter_by(box_id=_id).first()

    @classmethod
    def filter_string(cls, string, extra_chars=''):
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if isinstance(value, basestring) and not value.strip().isdigit():
            raise ValueError("Price must be an integer")
        else:
            value = int(value)
        if value < 1:
            raise ValueError("Price must be at least 1")
        self._price = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = unicode(value[:1024])

    def to_dict(self):
        return {
            'file_name': self.file_name,
            'price': self.price,
            'description': self.description,
        }
