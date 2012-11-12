# -*- coding: utf-8 -*-
'''
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
'''


import json

from uuid import uuid4
from sqlalchemy import Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import String
from models import dbsession, snapshot_to_snapshot_team
from models.BaseGameObject import BaseObject


class Snapshot(BaseObject):
    ''' Snapshot of game data '''

    # Has many 'SnapshotTeam' objects
    teams = relationship("SnapshotTeam", secondary=snapshot_to_snapshot_team, backref=backref("Snapshot", lazy="joined"))
    
    @property
    def key(self):
        return self.to_key(self.id)

    def to_dict(self):
        data = {}
        for team in self.teams:
            data[str(team.name)] = {
                'money': team.money,
                'game_levels': [str(level) for level in team.game_levels],
                'flags': [str(flag) for flag in team.flags],
            }
        return data

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, identifier):
        ''' Returns a the object with id of identifier '''
        return dbsession.query(cls).filter_by(id=identifier).first()

    @classmethod
    def to_key(cls, val):
        return 'snapshot.%d' % val
