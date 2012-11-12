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

from uuid import uuid4
from models import Team
from datetime import datetime
from libs.Singleton import Singleton
from libs.GameHistory import GameHistory


@Singleton
class ScoreboardManager(object):
    ''' Manages websocket connections (mostly thread safe) '''

    connections = {}

    def __init__(self):
        self.lock = threading.Lock()
        self.uuid = str(uuid4())
        self.history = GameHistory.Instance()

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

    def send_history(self, wsocket, count=10):
        if 0 < count: 
            count *= -1 
        wsocket.write_message(self.history[count:])

    def refresh(self):
        ''' Check for new notifications and send them to clients '''
        self.history.take_snapshot()
        self.lock.acquire()
        connections = dict(self.connections)
        for wsocket in connections:
            wsocket.write_message(self.history[-1])
        self.lock.release()
