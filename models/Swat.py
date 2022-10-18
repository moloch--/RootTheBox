# -*- coding: utf-8 -*-
"""
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
"""


from uuid import uuid4
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.sql import and_
from sqlalchemy.types import Integer, Boolean, String
from models import dbsession
from models.User import User
from models.BaseModels import DatabaseObject
from tornado.options import options
from builtins import str


class Swat(DatabaseObject):

    """
    Holds the bribe history of players that get 'SWAT'd
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    paid = Column(Integer, nullable=False)
    accepted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def all_pending(cls):
        return (
            dbsession.query(cls)
            .filter(and_(cls.accepted == False, cls.completed == False))
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def all_in_progress(cls):
        return (
            dbsession.query(cls)
            .filter(and_(cls.accepted == True, cls.completed == False))
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def all_completed(cls):
        return (
            dbsession.query(cls)
            .filter_by(completed=True)
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def pending_by_target_id(cls, uid):
        return (
            dbsession.query(cls)
            .filter_by(completed=False)
            .filter(and_(cls.accepted == False, cls.target_id == uid))
            .all()
        )

    @classmethod
    def in_progress_by_target_id(cls, uid):
        return (
            dbsession.query(cls)
            .filter(and_(cls.accepted == True, cls.completed == False))
            .filter_by(target_id=uid)
            .all()
        )

    @classmethod
    def by_id(cls, ident):
        """Returns a the object with id of ident"""
        return dbsession.query(cls).filter_by(id=ident).first()

    @classmethod
    def by_uuid(cls, uuid):
        """Returns a the object with given uuid"""
        return dbsession.query(cls).filter_by(uuid=uuid).first()

    @classmethod
    def by_user_id(cls, uid):
        """Return all objects based on user id"""
        return dbsession.query(cls).filter_by(user_id=uid).all()

    @classmethod
    def by_target_id(cls, uid):
        """Return all objects based on target id"""
        return dbsession.query(cls).filter_by(target_id=uid).all()

    @classmethod
    def count_completed_by_target_id(cls, uid):
        """Return the number of completed bribes in database"""
        return (
            dbsession.query(cls)
            .filter(and_(cls.completed == True, cls.target_id == uid))
            .count()
        )

    @classmethod
    def ordered(cls):
        """Return all bribes in chronological order"""
        return dbsession.query(cls).order_by(desc(cls.created)).all()

    @classmethod
    def ordered_by_user_id(cls, uid):
        """Return all bribes for user id in chronological order"""
        return (
            dbsession.query(cls)
            .filter_by(user_id=uid)
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def ordered_by_target_id(cls, uid):
        """Return all bribes for target id in chronological order"""
        return (
            dbsession.query(cls)
            .filter_by(target_id=uid)
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def get_price(cls, user):
        """Calculate price of next bribe based on history"""
        base_price = options.bribe_cost
        return base_price + (cls.count_completed_by_target_id(user.id) * base_price)

    @classmethod
    def user_is_pending(cls, user):
        """
        Return bool based on if there are any pending bribes in database
        """
        return 0 < len(cls.pending_by_target_id(user.id))

    @classmethod
    def user_is_in_progress(cls, user):
        """Returns bool based on if a user had a bribe in progress"""
        return 0 < len(cls.in_progress_by_target_id(user.id))

    @property
    def user(self):
        return User.by_id(self.user_id)

    @property
    def target(self):
        return User.by_id(self.target_id)

    def is_pending(self):
        return True if not self.accepted and not self.completed else False

    def is_in_progress(self):
        return True if self.accepted and not self.completed else False

    def is_declined(self):
        return True if not self.accepted and self.completed else False

    def is_successful(self):
        return True if self.accepted and self.completed else False

    def __repr__(self):
        return "<SWAT user_id: %d, target_id: %d" % (self.user_id, self.target_id)
