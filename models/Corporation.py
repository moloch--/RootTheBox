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
from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer
from sqlalchemy.orm import relationship, backref
from models import dbsession
from models.BaseGameObject import BaseObject


class Corporation(BaseObject):
    ''' Corporation definition '''

    name = Column(Unicode(64), unique=True, nullable=False)
    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    description = Column(Unicode(1024), nullable=False)
    boxes = relationship("Box", backref=backref(
        "Corporation", lazy="joined"), cascade="all, delete-orphan")

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
        return dbsession.query(cls).filter_by(name=corp_name).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return an object based on uuid '''
        return dbsession.query(cls).filter_by(uuid=uuid).first()

    def to_dict(self):
        ''' Returns editable data as a dictionary '''
        return dict(
            name=self.name, 
            description=self.description
        )
