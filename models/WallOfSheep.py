# -*- coding: utf-8 -*-
"""
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
"""


from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.types import Integer, Unicode
from models import dbsession
from models.User import User
from models.BaseModels import DatabaseObject


class WallOfSheep(DatabaseObject):

    """
    Stores a record of cracked passwords, and publicly displays
    them for all to see.
    """

    preimage = Column(Unicode(32), nullable=False)
    value = Column(Integer, nullable=False)
    victim_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    cracker_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    @classmethod
    def all(cls):
        """Returns all team objects"""
        return dbsession.query(cls).all()

    @classmethod
    def all_order_created(cls):
        """Returns all team objects"""
        return dbsession.query(cls).order_by(desc(cls.created)).all()

    @classmethod
    def all_order_value(cls):
        """Returns all team objects"""
        return dbsession.query(cls).order_by(desc(cls.value)).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_victim_id(cls, _id):
        """Returns all entries for a _id"""
        return dbsession.query(cls).filter_by(victim_id=_id).all()

    @classmethod
    def by_cracker_id(cls, _id):
        """Returns all entries for cracker_id"""
        return dbsession.query(cls).filter_by(cracker_id=_id).all()

    @classmethod
    def count_cracked_by(cls, _id):
        return dbsession.query(cls).filter_by(cracker_id=_id).count()

    @classmethod
    def leaderboard(cls, order_by="passwords"):
        """
        Creates an ordered list of tuples, for each user and the
        number of password they've cracked
        """
        orders = {"passwords": 1, "cash": 2}
        leaders = []
        for user in User.all_users():
            if 0 < cls.count_cracked_by(user.id):
                leaders.append(
                    (
                        user,
                        cls.count_cracked_by(user.id),
                        sum(cls.by_cracker_id(user.id)),
                    )
                )
        if order_by not in orders:
            order_by = "passwords"
        leaders.sort(key=lambda stats: stats[orders[order_by]], reverse=True)
        return leaders

    @property
    def victim(self):
        """Returns display name of user"""
        return User.by_id(self.victim_id)

    @property
    def cracker(self):
        """Returns display name of cracker"""
        return User.by_id(self.cracker_id)

    def __cmp__(self, other):
        """Used for sorting"""
        return len(self) - len(other)

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __repr__(self):
        return "<WallOfSheep - preimage: %s, victim_id: %d>" % (
            self.preimage,
            self.victim_id,
        )

    def __len__(self):
        return len(self.preimage)

    def __radd__(self, other):
        return self.value + other

    def __add__(self, other):
        return self.value + other.value
