# -*- coding: utf-8 -*-
'''
Created on Aug 27, 2013

@author: lavalamp

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

#TODO fill this file out, will contain a DB object reflecting sponsors for flags

from uuid import uuid4
from sqlalchemy import Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode, String
from models import DBSession
from models.BaseModels import DatabaseObject


class Sponsor(DatabaseObject):
    ''' Sponsor Definition '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    url = Column(Unicode(256), unique=False, nullable=True)
    name = Column(Unicode(128), unique=True, nullable=False)
    description = Column(Unicode(1024), unique=False, nullable=False)

    #TODO check to see if there are additional attributes that should be supplied to backref
    #sponsored_boxes = relationship("Box", backref="sponsor")

    @classmethod
    def all(cls):
        ''' Returns a list of all sponsor objects in the database '''
        return DBSession().query(cls).all()

    @classmethod
    def by_name(cls, _name):
        ''' Returns a sponsor by the sponsor's name '''
        #TODO constraints around sponsor name for search purposes
        return DBSession().query(cls).filter_by(name=_name).first()