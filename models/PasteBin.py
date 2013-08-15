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
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Unicode, Integer, String
from models import dbsession
from models.BaseGameObject import BaseObject


class PasteBin(BaseObject):
    ''' PasteBin definition '''

    name = Column(Unicode(32), nullable=False)
    contents = Column(Unicode(8192), nullable=False)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_uuid(cls, paste_uuid):
        ''' Get a paste object by uuid '''
        return dbsession.query(cls).filter_by(uuid=paste_uuid).first()

    @classmethod
    def by_team_id(cls, team_id):
        ''' Return all paste objects for a given team '''
        return dbsession.query(cls).filter_by(team_id=team_id).order_by(desc(cls.created)).all()

    def __str__(self):
        return self.name

    def __repr__(self):
        return ('<PasteBin - name:%s, user_id:%d>' % (self.name, self.user_id))
