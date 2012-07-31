# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

@author: moloch

 Copyright [2012] [Redacted Labs]

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

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer
from models.BaseGameObject import BaseObject
from models import team_challenges, dbsession


class Challenge(BaseObject):
    ''' Challenge definition '''

    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(1024), nullable=False)
    token = Column(Unicode(255), nullable=False)
    value = Column(Integer, nullable=False)
    teams = relationship(
        "Team", secondary=team_challenges, backref="Challenge")

    @classmethod
    def get_all(cls):
        ''' Returns all challenge objects '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, challenge_id):
        ''' Returns all challenge objects '''
        return dbsession.query(cls).filter_by(id=challenge_id).first()

    def __repr__(self):
        return ('<Challenge - name:%s, value:%d>' % (self.name, self.value))

    def __radd__(self, other):
        return self.value + other
