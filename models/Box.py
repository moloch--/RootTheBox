# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2012

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


from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref, synonym
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.BaseGameObject import BaseObject
from models import association_table


class Box(BaseObject):
    ''' Box definition '''

    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    corporation_id = Column(
        Integer, ForeignKey('corporation.id'), nullable=False)
    name = Column(Unicode(64), unique=True, nullable=False)
    ip_address = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(2048))
    difficulty = Column(Unicode(255), nullable=False)
    avatar = Column(Unicode(64), default=u"default_avatar.gif")
    root_key = Column(Unicode(64), unique=True, nullable=False)
    root_award = Column(Integer, nullable=False)
    user_key = Column(Unicode(64), unique=True, nullable=False)
    user_reward = Column(Integer, nullable=False)
    teams = relationship("Team", secondary=association_table, backref="Box")

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_name(cls, name):
        ''' Return the box object whose name is "name" '''
        return dbsession.query(cls).filter_by(name=unicode(name)).first()

    @classmethod
    def by_ip_address(cls, ip_address):
        ''' Return the box object whose ip is "ip_address" '''
        return dbsession.query(cls).filter_by(ip_address=unicode(ip_address)).first()

    def __repr__(self):
        return u'<Box - name: %s, root_value: %d, user_value: %d>' % (self.box_name, self.root_key, self.user_key)

    def __unicode__(self):
        return self.box_name
