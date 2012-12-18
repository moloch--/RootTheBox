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


import pylibmc
import logging

from models import dbsession, Snapshot, SnapshotTeam, Team
from sqlalchemy import desc
from libs.EventManager import EventManager
from libs.Singleton import Singleton
from libs.SecurityDecorators import async


@Singleton
class GameHistory(object):
    '''
    List-like object to store game history, with cache to avoid
    multiple large database reads.
    '''

    def __init__(self):
        self.cache = pylibmc.Client(['127.0.0.1'], binary=True)
        self.epoch = None  # Date/time of first snapshot
        self.__load__()
        self.event_manager = EventManager.Instance()

    @async
    def __load__(self):
        ''' Moves snapshots from db into the cache '''
        logging.info("Loading game history from database ...")
        if Snapshot.by_id(1) is None:
            self.__now__()  # Take starting snapshot
        self.epoch = Snapshot.by_id(1).created
        try:
            max_index = len(self)
            start_index = 1 if len(self) <= 10 else max_index - 9
            for index in range(start_index, max_index + 1):
                snapshot = Snapshot.by_id(index)
                if not snapshot.key in self.cache:
                    logging.info(
                        "Cached snapshot (%d of %d)" % (snapshot.id, max_index)
                    )
                    self.cache.set(snapshot.key, snapshot.to_dict())
            logging.info("History load complete.")
        except KeyboardInterrupt:
            logging.info("History load stopped by user.")

    def take_snapshot(self):
        ''' Take a snapshot of the current game data '''
        snapshot = self.__now__()
        self.cache.set(snapshot.key, snapshot.to_dict())
        self.event_manager.push_history(snapshot.to_dict())

    def get_flag_history_by_name(self, name, start, stop=None):
        snapshots = self[start:] if stop is None else self[start:stop]
        series = []
        for snapshot in snapshots:
            if name in snapshot['scoreboard']:
                flags = snapshot['scoreboard'][name]['flags']
                series.append((snapshot['timestamp'], len(flags),))
        return series

    def get_money_history_by_name(self, name, start, stop=None):
        snapshots = self[start:] if stop is None else self[start:stop]
        series = []
        for snapshot in snapshots:
            if name in snapshot['scoreboard']:
                money = snapshot['scoreboard'][name]['money']
                series.append((snapshot['timestamp'], money,))
        return series

    def __now__(self):
        ''' Returns snapshot object it as a dict '''
        snapshot = Snapshot()
        for team in Team.all():
            snapshot_team = SnapshotTeam(
                team_id=team.id,
                money=team.money,
            )
            snapshot_team.game_levels = team.game_levels
            snapshot_team.flags = team.flags
            dbsession.add(snapshot_team)
            dbsession.flush()
            snapshot.teams.append(snapshot_team)
        dbsession.add(snapshot)
        dbsession.flush()
        return snapshot

    def __iter__(self):
        for snapshot in self:
            yield snapshot.to_dict()

    def __contains__(self, index):
        return True if Snapshot.by_id(index) is not None else False

    def __len__(self):
        ''' Return length of the game history '''
        return dbsession.query(Snapshot).order_by(desc(Snapshot.id)).first().id

    def __getitem__(self, key):
        ''' Implements slices and indexs '''
        if isinstance(key, slice):
            ls = [self[index] for index in xrange(*key.indices(len(self)))]
            return filter(lambda item: item is not None, ls)
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self)
            if key >= len(self):
                raise IndexError("The index (%d) is out of range." % key)
            return self.__at__(key)
        else:
            raise TypeError("Invalid index argument to GameHistory")

    def __at__(self, index):
        ''' Get snapshot at specific index '''
        key = Snapshot.to_key(index + 1)
        if key in self.cache:
            return self.cache.get(key)
        else:
            snapshot = Snapshot.by_id(index + 1)
            if snapshot is not None:
                self.cache.set(snapshot.key, snapshot.to_dict())
                return snapshot.to_dict()
        return None
