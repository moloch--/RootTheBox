# -*- coding: utf-8 -*-
'''
Created on Mar 21, 2012

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


from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Integer, Unicode
from models import dbsession, User
from models.BaseGameObject import BaseObject


class WallOfSheep(BaseObject):

    preimage = Column(Unicode(64), nullable=False)
    point_value = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    cracker_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    @property
    def user(self):
        ''' Returns display name of user'''
        return User.by_id(self.user_id)

    @property
    def cracker(self):
        ''' Returns display name of cracker '''
        return User.by_id(self.cracker_id)

    @classmethod
    def get_all(cls):
        ''' Returns all team objects '''
        return dbsession.query(cls).order_by(desc(cls.created)).all()

    @classmethod
    def by_user_id(cls, user_id):
        ''' Returns all entries for a user_id '''
        return dbsession.query(cls).filter_by(user_id=user_id).all()

    @classmethod
    def by_cracker_id(cls, cracker_id):
        ''' Returns all entries for cracker_id '''
        return dbsession.query(cls).filter_by(cracker_id=cracker_id).all()

    def __repr__(self):
        return ('<WallOfSheep - preimage: %s, user_id: %d>' % (self.preimage, self.user_id)).encode('utf-8')
