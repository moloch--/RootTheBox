# -*- coding: utf-8 -*-
"""
Created on Jun 22, 2018

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

from uuid import uuid4
from sqlalchemy import Column, ForeignKey, asc
from sqlalchemy.sql import and_
from sqlalchemy.types import Unicode, String, Integer
from models import dbsession
from models.BaseModels import DatabaseObject
from builtins import str


class FlagChoice(DatabaseObject):

    """Flag Choice definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    flag_id = Column(Integer, ForeignKey("flag.id"), nullable=False)
    _choice = Column(Unicode(256), nullable=True)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).filter_by(team_id=None).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Returns a the object with id of _uuid"""
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_flag_id(cls, _id):
        """Return choices for a flag"""
        return (
            dbsession.query(cls).filter_by(flag_id=_id).order_by(asc(cls.created)).all()
        )

    @classmethod
    def by_count(cls, flag):
        """Return choices count for a team and flag"""
        return dbsession.query(cls).filter(and_(cls.flag_id == flag.id).count())

    @classmethod
    def create_choice(cls, flag=None, item=None):
        """Create a choice and save it to the database"""
        if not flag:
            flag = cls.flag
        if not item:
            return
        choice = cls._create(flag, str(item)[:256])
        dbsession.add(choice)
        dbsession.commit()

    @classmethod
    def _create(cls, flag, choice):
        """Create a choice and save it to the database"""
        logging.debug("Creating flag '%s' choice" % (flag.id))
        return cls(flag_id=flag.id, _choice=choice)

    @property
    def choice(self):
        return str(self._choice)

    @choice.setter
    def choice(self, value):
        self._choice = value[:256]

    def to_dict(self):
        """Return public data as dict"""
        return {"uuid": self.uuid, "choice": self.choice}
