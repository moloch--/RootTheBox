# -*- coding: utf-8 -*-
'''
Created on Sep 20, 2012

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


import re

from datetime import datetime
from libs.Singleton import Singleton
from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer, Unicode
from sqlalchemy.ext.declarative import declared_attr, declarative_base



class MemoryDatabaseObject(object):
    '''
    In memory base object
    '''

    @declared_attr
    def __tablename__(self):
        ''' Converts class name from camel case to snake case '''
        name = self.__name__
        return (
            name[0].lower() +
            re.sub(r'([A-Z])',
                   lambda letter: "_" + letter.group(0).lower(), name[1:])
        )
    
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    created = Column(DateTime, default=datetime.now)


class Bot(MemoryDatabaseObject):
    '''
    Bot Class 
    '''
    wsock_uuid = Column(String(36), nullable=False)
    team_uuid = Column(String(36), nullable=False)
    box_uuid = Column(String(36), nullable=False)
    remote_ip = Column(String(36), nullable=False)



@Singleton
class BotManager(object):
    '''
    Holds refs to botnet web socket objects
    '''

    def __init__(self):
        self.botnet = {}  # Holds refs to wsockets
        self.sqlite_engine = create_engine('sqlite://')
        setattr(self.sqlite_engine, 'echo', False)
        Session = sessionmaker(bind=self.sqlite_engine, autocommit=True)
        self.botdb = Session(autoflush=True)
        baseObject = declarative_base(cls=MemoryDatabaseObject)
        baseObject.metadata.create_all(self.sqlite_engine)

    def by_box(self, box):
        bots = self.botdb.dbquery(Bot).filter_by(box_uuid=box.uuid).all()
        return [self.botnet[bot.uuid] for bot in bots]

    def by_team(self, team):
        bots = self.botdb.dbquery(Bot).filter_by(team_uuid=team.uuid).all()
        return [self.botnet[bot.uuid] for bot in bots]

    def count_team(self, team):
        return self.botdb.dbquery(Bot).filter_by(team_uuid=team.uuid).count()

    def add_bot(self, bot_wsocket):
        if not self.is_duplicate():
            bot = Bot(
                wsock_uuid=bot_wsocket.uuid
                team_uuid=bot_wsocket.team_uuid,
                box_uuid=bot_wsocket.box_uuid,
                remote_ip=bot_wsocket.remote_ip
            )
            self.botdb.add(bot)
            self.botdb.flush()
            self.botnet[bot_wsocket.uuid] = bot_wsocket

    def remove_bot(self, bot_wsocket):
        bot = self.botdb.dbquery(Bot).filter_by(wsock_uuid=bot_wsocket.uuid)
        self.botdb.delete(bot)
        self.botdb.flush()
        self.botnet.remove(bot_wsocket)

    def is_duplicate(self, bot_wsocket):
        return 0 < self.botdb.query(Bot).filter(
            and_(Bot.team_uuid == bot_wsocket.team_uuid, Bot.box_uuid == bot_wsocket.box_uuid)
        ).count()