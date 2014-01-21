# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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


from uuid import uuid4
from random import randint
from sqlalchemy import Column
from sqlalchemy.orm import relationship, backref, synonym
from sqlalchemy.types import Integer, Unicode, String
from models import dbsession, team_to_box, team_to_item,   \
    team_to_flag, team_to_game_level, team_to_source_code, \
    team_to_hint
from models.BaseGameObject import BaseObject
from string import ascii_letters, digits
from libs.BotManager import BotManager


class Team(BaseObject):
    ''' Team definition '''

    _name = Column(Unicode(16), unique=True, nullable=False)
    name = synonym('_name', descriptor=property(
        lambda self: self._name,
        lambda self, name: setattr(
            self, '_name', self.__class__.filter_string(name, " -_"))
    ))
    motto = Column(Unicode(32))

    members = relationship("User",
        backref=backref("Team", lazy="joined"),
        cascade="all, delete-orphan")

    files = relationship("FileUpload", backref=backref("Team", lazy="select"))
    pastes = relationship("PasteBin", backref=backref("Team", lazy="select"))
    money = Column(Integer, default=500, nullable=False)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    flags = relationship("Flag",
        secondary=team_to_flag,
        backref=backref("Team", lazy="select"))

    boxes = relationship("Box",
        secondary=team_to_box,
        backref=backref("Team", lazy="select"))

    items = relationship("MarketItem",
        secondary=team_to_item,
        backref=backref("Team", lazy="joined"))

    purchased_source_code = relationship("SourceCode",
        secondary=team_to_source_code,
        backref=backref("Team", lazy="select"))

    hints = relationship("Hint",
        secondary=team_to_hint,
        backref=backref("Team", lazy="select"))

    game_levels = relationship("GameLevel",
        secondary=team_to_game_level,
        backref=backref("Team", lazy="select"))

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def ranks(cls):
        ''' Returns a list of all objects in the database '''
        return sorted(dbsession.query(cls).all())

    @classmethod
    def by_id(cls, identifier):
        ''' Returns a the object with id of identifier '''
        return dbsession.query(cls).filter_by(id=identifier).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_name(cls, team_name):
        ''' Return the team object based on "team_name" '''
        return dbsession.query(cls).filter_by(name=unicode(team_name)).first()

    @classmethod
    def filter_string(cls, string, extra_chars=''):
        char_white_list = ascii_letters + digits + extra_chars
        clean = filter(lambda char: char in char_white_list, string)
        return clean if 0 < len(clean) else 'foobar'

    @property
    def levels(self):
        ''' Sorted game_levels '''
        return sorted(self.game_levels)

    def level_flags(self, lvl):
        ''' Given a level number return all flags captured for that level '''
        return filter(lambda flag: flag.game_level.number == lvl, self.flags)

    @property
    def bot_count(self):
        bot_manager = BotManager.Instance()
        return bot_manager.count_by_team_uuid(self.uuid)

    def to_dict(self):
        ''' Use for JSON related tasks; return public data only '''
        return {
            'name': self.name,
            'motto': self.motto,
            'money': self.money,
        }

    def file_by_file_name(self, file_name):
        ''' Return file object based on file_name '''
        ls = self.files.filter_by(file_name=file_name)
        return ls[0] if 0 < len(ls) else None

    def __repr__(self):
        return u'<Team - name: %s, money: %d>' % (self.name, self.money)

    def __str__(self):
        return self.name.encode('ascii', 'ignore')

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        if len(self.flags) < len(other.flags):
            return 1
        elif len(self.flags) == len(other.flags):
            return 0
        else:
            return -1
