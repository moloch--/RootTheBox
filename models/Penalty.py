# -*- coding: utf-8 -*-
"""
Created on Jun 5, 2018

@author: ElJefe

    Copyright 2018 Root the Box

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

import logging

from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.sql import and_
from sqlalchemy.types import Unicode, String, Integer, Boolean
from models import dbsession
from models.User import User
from models.BaseModels import DatabaseObject


class Penalty(DatabaseObject):

    """ Penalty definition """

    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))
    flag_id = Column(Integer, ForeignKey("flag.id", ondelete="CASCADE"))
    _token = Column(Unicode(256), nullable=True)

    @classmethod
    def all(cls):
        """ Returns a list of all objects in the database """
        return dbsession.query(cls).filter_by(team_id=None).all()

    @classmethod
    def clear(cls):
        """ Deletes all objects in the database """
        return dbsession.query(cls).delete()

    @classmethod
    def by_id(cls, _id):
        """ Returns a the object with id of _id """
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_team_id(cls, _id):
        """ Return penalties for a team """
        return (
            dbsession.query(cls)
            .filter_by(team_id=_id)
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def by_flag_id(cls, _id):
        """ Return penalties for a flag """
        return (
            dbsession.query(cls)
            .filter_by(flag_id=_id)
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def by_count(cls, flag, team):
        """ Return penalty count for a team and flag """
        if not team:
            return 0
        return (
            dbsession.query(cls)
            .filter(and_(cls.flag_id == flag.id, cls.team_id == team.id))
            .count()
        )

    @classmethod
    def by_token_count(cls, flag, team, submission):
        """ Return count for existing team token """
        return (
            dbsession.query(cls)
            .filter(
                and_(
                    cls.flag_id == flag.id,
                    cls.team_id == team.id,
                    cls._token == submission,
                )
            )
            .count()
        )

    @classmethod
    def create_attempt(cls, team=None, flag=None, submission=None):
        attempt = cls._create(team, flag, submission)
        dbsession.add(attempt)
        dbsession.commit()

    @property
    def token(self):
        return self._token

    @classmethod
    def _create(cls, team, flag, submission):
        """ Create a attempt and save it to the database """
        if not team:
            team = cls.team
        if not flag:
            flag = cls.flag
        if not submission:
            submission = ""
        logging.debug("Creating flag '%s' attempt for %r" % (flag.id, team.name))
        attempt = Penalty(team_id=team.id, flag_id=flag.id, _token=submission)
        return attempt

    def to_dict(self):
        """ Return public data as dict """
        return {"token": self.token}
