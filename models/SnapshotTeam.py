# -*- coding: utf-8 -*-
"""
Created on Mar 11, 2012

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


from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer
from models import dbsession
from models.Team import Team
from models.Relationships import snapshot_team_to_flag, snapshot_team_to_game_level
from models.BaseModels import DatabaseObject


class SnapshotTeam(DatabaseObject):

    """
    Used by game history; snapshot of a single team in history
    """

    team_id = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"), nullable=False)
    money = Column(Integer, nullable=False)
    bots = Column(Integer, nullable=False)

    game_levels = relationship(
        "GameLevel",
        secondary=snapshot_team_to_game_level,
        backref=backref("snapshot_team", lazy="select"),
    )

    flags = relationship(
        "Flag",
        secondary=snapshot_team_to_flag,
        backref=backref("snapshot_team", lazy="select"),
    )

    @property
    def name(self):
        return dbsession.query(Team._name).filter_by(id=self.team_id).first()[0]

    @classmethod
    def all(cls):
        """ Returns a list of all objects in the database """
        return dbsession.query(cls).all()
