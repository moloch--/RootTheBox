'''
Created on Nov 11, 2012

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
import pylibmc
import logging

from uuid import uuid4
from models import dbsession, Snapshot, Team
from sqlalchemy import func 
from libs.Singleton import Singleton


@Singleton
class GameHistory():
    '''
    List-like object to store game history, with cache to avoid
    multiple large database reads.
    '''

    def __init__(self):
        self.cache = pylibmc.Client(['127.0.0.1'], binary=True)
        self.__load__()

    def __load__(self):
        ''' Moves snapshots from db into the cache '''
        logging.debug("Loading snapshots from database ...")
        for snapshot in Snapshot.all():
            if not snapshot.key in self.cache:
                self.cache.set(snapshot.key, snapshot.game_data)

    def take_snapshot(self):
        ''' Take a snapshot of the current game data '''
        logging.debug("Taking game data snapshot.")
        snapshot = Snapshot(
            game_data=json.dumps(self.now()),
        )
        dbsession.add(snapshot)
        dbsession.flush()
        self.cache.set(snapshot.key, snapshot.game_data)
        return snapshot
    
    def now(self):
        ''' Gets game data returns it as a dict '''
        data = {}
        for team in Team.all():
            data[team.name] = {
                'money': int(team.money),
                'flags': [flag.name for flag in team.flags],
                'levels': [level.number for level in team.game_levels],
            }
        return data

    def __len__(self):
        return dbsession.query(func.max(Snapshot.id)) 

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[index] for index in xrange(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0: # Handle negative indices
                key += len(self)
            if key >= len(self):
                raise IndexError("The index (%d) is out of range." % key)
            return self.__at__(key)
        else:
            raise TypeError("Invalid index argument to GameHistory")

    def __at__(self, index):
        ''' Get snapshot at specific index '''
        if Snapshot.to_key(index) in self.cache:
            return self.cache.get(key)
        else:
            snapshot = Snapshot.by_id(key)
            self.cache.set(snapshot.key, snapshot.game_data)
            return snapshot
