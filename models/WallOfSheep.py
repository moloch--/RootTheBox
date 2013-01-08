# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2012

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


from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Integer, Unicode, String
from models import dbsession, User
from models.BaseGameObject import BaseObject


class WallOfSheep(BaseObject):

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: uuid4())
    preimage = Column(Unicode(16), nullable=False)
    value = Column(Integer, nullable=False)
    victim_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    cracker_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    @property
    def user(self):
        ''' Returns display name of user'''
        return User.by_id(self.victim_id)

    @property
    def cracker(self):
        ''' Returns display name of cracker '''
        return User.by_id(self.cracker_id)

    @classmethod
    def all(cls):
        ''' Returns all team objects '''
        return dbsession.query(cls).order_by(desc(cls.created)).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_victim_id(cls, victim_id):
        ''' Returns all entries for a victim_id '''
        return dbsession.query(cls).filter_by(victim_id=victim_id).all()

    @classmethod
    def by_cracker_id(cls, cracker_id):
        ''' Returns all entries for cracker_id '''
        return dbsession.query(cls).filter_by(cracker_id=cracker_id).all()

    def __repr__(self):
        return u'<WallOfSheep - preimage: %s, victim_id: %d>' % (
            self.preimage, self.victim_id
        )
