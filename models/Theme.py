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
from string import ascii_letters, digits
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.types import Unicode, Integer, Boolean
from models.BaseGameObject import BaseObject
from models import dbsession


class Theme(BaseObject):
    '''
    Holds theme related settings
    '''

    _name = Column(Unicode(64), unique=True, nullable=False)
    name = synonym('_name', descriptor=property(
        lambda self: self._name,
        lambda self, name: setattr(self, '_name',
                                        self.__class__._filter_string(name))
    ))
    _cssfile = Column(Unicode(64), unique=True, nullable=False)
    cssfile = synonym('_cssfile', descriptor=property(
        lambda self: self._cssfile,
        lambda self, cssfile: setattr(self, '_cssfile',
                                        self.__class__._filter_string(cssfile, "."))
    ))
    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))

    @classmethod
    def all(cls):
        ''' Return all objects '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Return the object whose id is ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_uuid(cls, f_uuid):
        ''' Return the object whose uuid is f_uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(f_uuid)).first()

    @classmethod
    def by_name(cls, theme_name):
        ''' Return the object whose name is theme_name '''
        return dbsession.query(cls).filter_by(name=theme_name).first()

    @classmethod
    def by_cssfile(cls, file_name):
        ''' Return the object whose name is theme_name '''
        return dbsession.query(cls).filter_by(cssfile=file_name).first()

    @classmethod
    def _filter_string(cls, string, extra_chars=""):
        ''' Remove any non-white listed chars from a string '''
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)