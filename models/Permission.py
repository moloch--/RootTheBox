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

from sqlalchemy.types import Unicode, Integer
from sqlalchemy import Column, ForeignKey
from models import dbsession
from models.BaseGameObject import BaseObject


class Permission(BaseObject):
    ''' Permission definition '''

    name = Column(Unicode(64), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    def __repr__(self):
        return u'<Permission - name: %s, user_id: %d>' % (self.name, self.user_id)

    def __unicode__(self):
        return self.name
