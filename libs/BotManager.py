# -*- coding: utf-8 -*-
"""
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
-----------------------------------------------------

Not gonna sugar code it, this shit gets a bit complicated.

"""
# pylint: disable=no-member


import re
import os
import logging

from datetime import datetime
from libs.Singleton import Singleton
from builtins import str
from sqlalchemy import Column, create_engine
from sqlalchemy.sql import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import DateTime, Integer, Unicode
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from tempfile import NamedTemporaryFile
from models import dbsession
from models.Box import Box
from tornado.options import options


class _BotDatabaseObject(object):
    """
    Base object for in-memory database
    """

    @declared_attr
    def __tablename__(self):
        """Converts class name from camel case to snake case"""
        name = self.__name__
        return str(
            name[0].lower()
            + re.sub(r"([A-Z])", lambda letter: "_" + letter.group(0).lower(), name[1:])
        )

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    created = Column(DateTime, default=datetime.now)


BotDatabaseObject = declarative_base(cls=_BotDatabaseObject)


class Bot(BotDatabaseObject):
    """Bot Class"""

    last_ping = Column(DateTime, default=datetime.now)
    wsock_uuid = Column(Unicode(36), nullable=False)
    team_uuid = Column(Unicode(36), nullable=False)
    box_uuid = Column(Unicode(36), nullable=False)
    remote_ip = Column(Unicode(36), nullable=False)
    total_reward = Column(Integer, default=0, nullable=False)

    # Used for easy lookups
    team_name = Column(Unicode(64), nullable=False)
    box_name = Column(Unicode(64), nullable=False)

    @property
    def box(self):
        """Pull box object from persistent db"""
        return dbsession.query(Box).by_uuid(self.box_uuid)

    @property
    def team(self):
        """Pull box object from persistent db"""
        return dbsession.query(Box).by_uuid(self.box_uuid)

    def to_dict(self):
        return {
            "team_name": self.team_name,
            "last_ping": str(self.last_ping),
            "total_reward": self.total_reward,
            "box_name": self.box_name,
            "remote_ip": self.remote_ip,
        }


@Singleton
class BotManager(object):
    """
    This is an observable class.

    Holds refs to botnet web socket handler objects.
    Holds refs to botnet monitor handler objects (observers).
    """

    def __init__(self):
        self.botnet = {}  # Holds refs to wsockets
        self.monitors = {}
        if options.botnet_db == ":tempfile:":
            options.botnet_db = NamedTemporaryFile(delete=False).name
        if os.path.exists(options.botnet_db):
            os.remove(options.botnet_db)
            logging.debug("Removing old botnet database file")
        self.db_path = "sqlite:///%s" % options.botnet_db
        logging.debug("Created botnet database at: %s" % self.db_path)
        self.sqlite_engine = create_engine(self.db_path, echo=options.log_sql)
        Session = sessionmaker(bind=self.sqlite_engine, autocommit=True)
        self.botdb = Session(autoflush=True)
        BotDatabaseObject.metadata.create_all(self.sqlite_engine)
        self.dbsession = dbsession

    def all(self):
        return self.botdb.query(Bot).all()

    def by_box(self, box):
        bots = self.botdb.query(Bot).filter_by(box_uuid=str(box.uuid)).all()
        return [self.botnet[bot.wsock_uuid] for bot in bots]

    def by_team(self, team):
        bots = self.botdb.query(Bot).filter_by(team_name=str(team)).all()
        return [self.botnet[bot.wsock_uuid] for bot in bots]

    def count_all_teams(self):
        from models.Team import Team

        teams = Team.all()
        botcount = {}
        for team in teams:
            botcount[team.uuid] = 0
        for bot in self.botdb.query(Bot).all():
            botcount[bot.team_uuid] += 1
        return botcount

    def count_by_team(self, team):
        return len(self.by_team(team))

    def count_by_team_uuid(self, tuuid):
        return self.botdb.query(Bot).filter_by(team_uuid=str(tuuid)).count()

    def add_bot(self, bot_wsocket):
        if not self.is_duplicate(bot_wsocket):
            from models.Team import Team

            bot = Bot(
                wsock_uuid=str(bot_wsocket.uuid),
                team_name=str(bot_wsocket.team_name),
                box_name=str(bot_wsocket.box_name),
                team_uuid=str(bot_wsocket.team_uuid),
                box_uuid=str(bot_wsocket.box_uuid),
                remote_ip=str(bot_wsocket.remote_ip),
            )
            team = Team.by_uuid(bot.team_uuid)
            bot.dbsession = self.dbsession
            self.botdb.add(bot)
            self.botdb.flush()
            self.botnet[bot_wsocket.uuid] = bot_wsocket

            team.set_bot(self.count_by_team_uuid(team.uuid))
            self.notify_monitors(team.name)
            return True
        else:
            return False

    def save_bot(self, bot):
        """Save changes to a bot and flush"""
        self.botdb.add(bot)
        self.botdb.flush()

    def remove_bot(self, bot_wsocket):
        bot = self.botdb.query(Bot).filter_by(wsock_uuid=str(bot_wsocket.uuid)).first()
        if bot is not None:
            from models.Team import Team

            team = Team.by_uuid(bot.team_uuid)
            logging.debug("Removing bot '%s' at %s" % (bot.team_uuid, bot.remote_ip))
            self.botnet.pop(bot_wsocket.uuid, None)
            self.botdb.delete(bot)
            self.botdb.flush()
            team.set_bot(self.count_by_team_uuid(team.uuid))
            self.notify_monitors(team.name)
        else:
            logging.warning(
                "Failed to remove bot '%s' does not exist in manager" % bot_wsocket.uuid
            )

    def is_duplicate(self, bot_wsocket):
        """Check for duplicate bots"""
        assert bot_wsocket.team_uuid is not None
        assert bot_wsocket.box_uuid is not None
        return (
            0
            < self.botdb.query(Bot)
            .filter(
                and_(
                    Bot.team_uuid == str(bot_wsocket.team_uuid),
                    Bot.box_uuid == str(bot_wsocket.box_uuid),
                )
            )
            .count()
        )

    def add_monitor(self, monitor_wsocket):
        """Add new monitor socket"""
        if monitor_wsocket.team_name not in self.monitors:
            self.monitors[monitor_wsocket.team_name] = []
        self.monitors[monitor_wsocket.team_name].append(monitor_wsocket)

    def remove_monitor(self, monitor_wsocket):
        """Remove a monitor socket"""
        if (
            monitor_wsocket.team_name in self.monitors
            and monitor_wsocket in self.monitors[monitor_wsocket.team_name]
        ):
            self.monitors[monitor_wsocket.team_name].remove(monitor_wsocket)

    def notify_monitors(self, team_name):
        """Update team monitors"""
        if team_name in self.monitors and 0 < len(self.monitors[team_name]):
            logging.debug("Sending update to %s" % team_name)
            bots = self.get_bots(team_name)
            for monitor in self.monitors[team_name]:
                monitor.update(bots)

    def get_bots(self, team):
        """Get info on boxes for a team"""
        bots = self.botdb.query(Bot).filter_by(team_name=str(team)).all()
        return [bot.to_dict() for bot in bots]

    def get_all_bots(self):
        """Get info on all bots"""
        bots = self.botdb.query(Bot).all()
        return [bot.to_dict() for bot in bots]

    def add_rewards(self, team, reward):
        """Add rewards to bot records"""
        bots = self.botdb.query(Bot).filter_by(team_name=str(team)).all()
        for bot in bots:
            bot.total_reward += reward
            self.botdb.add(bot)
            self.botdb.flush()

    def __del__(self):
        if os.path.exists(options.botnet_db):
            os.unlink(options.botnet_db)


def ping_bots():
    """Ping all websockets in database"""
    bot_manager = BotManager.instance()
    logging.debug("Pinging open botnet websockets")

    for bot in bot_manager.all():
        wsocket = bot_manager.botnet[bot.wsock_uuid]
        wsocket.ping()
        bot.last_ping = datetime.now()
        bot_manager.save_bot(bot)

    for muuid in bot_manager.monitors:
        for monitor in bot_manager.monitors[muuid]:
            monitor.ping()
