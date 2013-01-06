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


from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Integer, Boolean
from models import dbsession, User
from models.BaseGameObject import BaseObject


class Swat(BaseObject):
    ''' 
    Holds the bribe history of players that get 'SWAT'd 
    '''

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    paid = Column(Integer, nullable=False)
    accepted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def all_pending(cls):
        return dbsession.query(cls).filter_by(accepted=False).order_by(desc(cls.created)).all()

    @classmethod
    def by_id(cls, ident):
        ''' Returns a the object with id of ident '''
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_user_id(cls, uid):
        ''' Return all objects based on user id '''
        return dbsession.query(cls).filter_by(user_id=uid).all()

    @classmethod
    def by_target_id(cls, uid):
        ''' Return all objects based on target id '''
        return dbsession.query(cls).filter_by(target_id=uid).all()

    @classmethod
    def ordered(cls):
        ''' Return all bribes in chronological order '''
        return dbsession.query(cls).order_by(desc(cls.created)).all()

    @classmethod
    def ordered_user_id(cls, uid):
        ''' Return all bribes for user id in chronological order '''
        return dbsession.query(cls).filter_by(user_id=uid).order_by(desc(cls.created)).all()

    @classmethod
    def ordered_target_id(cls, uid):
        ''' Return all bribes for target id in chronological order '''
        return dbsession.query(cls).filter_by(target_id=uid).order_by(desc(cls.created)).all()

    @classmethod
    def get_price(cls, tid):
        ''' Calculate price of next bribe based on history '''
        config = ConfigManager.Instance()
        base_price = config.bribe_base_price
        return base_price + (len(cls.by_target_id(tid)) * base_price)

    def get_user_team(self):
        ''' Return user's team '''
        return User.by_id(self.user_id).team

    def get_target_team(self):
        ''' Return target's team '''
        return User.by_id(self.target_id).team

    def __state__(self):
        ''' Determine printable state '''
        if not self.accepted:
            return 'Pending'
        elif self.accepted and not self.completed:
            return 'Accepted/In Progress'
        elif self.accepted and self.completed:
            return 'Completed'
        else:
            raise ValueError("Cannot determine state")

    def __str__(self):
        return self.__state__()