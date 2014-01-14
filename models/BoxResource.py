# -*- coding: utf-8 -*-
'''
Created on Aug 29, 2013

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

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode, String
from models import DBSession
from models.BaseModels import DatabaseObject

class BoxResource(DatabaseObject):
    ''' BoxResource Definition '''

    #TODO sanitize these values
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    box_id = Column(Integer, ForeignKey('box.id'), nullable=True)
    url = Column(Unicode(512), unique=False, nullable=False)
    tag = Column(Unicode(128), unique=False, nullable=False)
    description = Column(Unicode(256), unique=False, nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all BoxResource objects in the database '''
        return DBSession.query(cls).all()