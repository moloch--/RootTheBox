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
from sqlalchemy.types import Unicode, Integer
from models import dbsession, Box
from models.BaseGameObject import BaseObject


class Flag(BaseObject):
    ''' Flag definition '''

    name = Column(Unicode(255), nullable=False)
    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    token = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255), nullable=False)
    value = Column(Integer, nullable=False)
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

    def to_dict(self):
        ''' Returns editable data as a dictionary '''
        box = Box.by_id(self.box_id)
        return dict(
            flag_name=self.name,
            flag_token=self.token,
            flag_description=self.description,
            flag_value=self.value,
            flag_box_uuid=box.uuid,
        )