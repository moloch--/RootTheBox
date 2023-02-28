"""
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
"""
# pylint: disable=no-member


import logging

from models import dbsession
from models.Team import Team
from sqlalchemy import desc
from libs.BotManager import BotManager
from libs.EventManager import EventManager
from libs.Sessions import MemcachedConnect
from libs.Singleton import Singleton
from tornado.options import options
from builtins import object, range


@Singleton
class GameHistory(object):
    """
    List-like object to store game history, with cache to avoid
    multiple large database reads.
    """

    def __init__(self):
        self.config = options
        self.dbsession = dbsession
        self.cache = MemcachedConnect()
        self.epoch = None  # Date/time of first snapshot
        self.event_manager = EventManager.instance()

    def _load(self):
        """Moves snapshots from db into the cache"""
        pass
        
