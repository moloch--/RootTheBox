# -*- coding: utf-8 -*-

'''
Created on Oct 04, 2012

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


import threading

from models import Team
from libs.Singleton import Singleton


@Singleton
class ScoreboardManager(object):
    ''' Manages websocket connections (mostly thread safe) '''

    connections = {}

    def __init__(self):
        self.lock = threading.Lock()

    @classmethod
    def refresh(cls):
        ''' Non-blocking call to __refresh__ '''
        manager = cls.Instance()
        threading.Thread(target=manager.__refresh__).start()

    def add_connection(self, wsocket):
        ''' Add a connection '''
        self.lock.acquire()
        if self.connections.has_key(wsocket.user_id):
            self.connections[wsocket.user_id].append(wsocket)
        else:
            self.connections[wsocket.user_id] = [wsocket]
        self.lock.release()

    def remove_connection(self, wsocket):
        ''' Remove connection '''
        self.lock.acquire()
        self.connections[wsocket.user_id].remove(wsocket)
        if len(self.connections[wsocket.user_id]) <= 0:
            del self.connections[wsocket.user_id]
        self.lock.release()

    def __refresh__(self):
        ''' Check for new notifications and send them to clients '''
        self.lock.acquire()
        connections = dict(self.connections)
        for wsocket in connections:
            wsocket.write_message(self.game_data)
        self.lock.release()

    @property
    def game_data(self):
        ''' Gets game data returns it as a dict '''
        data = {}
        for team in Team.all():
            data[team.name] = {
                'money': int(team.money),
                'flags': [flag.name for flag in team.flags],
                'levels': [level.number for level in team.game_levels],
            }
        return data
