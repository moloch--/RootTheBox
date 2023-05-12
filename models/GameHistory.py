# -*- coding: utf-8 -*-
"""
Created on Mar 3, 2023

@author: ElJefe

    Copyright 2023 Root the Box

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
# pylint: disable=no-member

import json
from models import dbsession
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, String, Integer
from models.BaseModels import DatabaseObject
from builtins import str
from tornado.options import options


class GameHistory(DatabaseObject):

    """Game History definition"""

    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    _type = Column(Unicode(20), nullable=False, default=str("none"))
    _value = Column(Integer, default=0, nullable=False)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_type(cls, _type):
        """Return the game history object based on the _type"""
        return dbsession.query(cls).filter_by(_type=_type).all()

    @classmethod
    def by_team(cls, _team_id):
        """Return the game history object based on the team"""
        return dbsession.query(cls).filter_by(team_id=_team_id).all()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, _type):
        self._type = str(_type)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        self._value = int(_value)

    def to_dict(self):
        from models.Team import Team

        team = Team.by_id(self.team_id)
        """Returns public data as a dict"""
        return {
            "timestamp": self.created.strftime("%s"),
            "team_name": team.name,
            "value": self._value,
        }

    def __repr__(self):
        return "<GameHistory - team_id: %d, type: %s, value: %d>" % (
            self.team_id,
            self._type,
            self._value,
        )

    def __str__(self):
        from models.Team import Team

        team = Team.by_id(self.team_id)
        return json.dumps(
            {
                "created": self.created.strftime("%s"),
                "team_uuid": team.uuid,
                "type": self._type,
                "value": self._value,
            }
        )
