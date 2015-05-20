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


import xml.etree.cElementTree as ET

from uuid import uuid4
from sqlalchemy import Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode, String
from models import dbsession
from models.BaseModels import DatabaseObject
from models.Relationships import team_to_box, team_to_item, \
    team_to_flag, team_to_game_level, team_to_source_code, \
    team_to_hint
from libs.BotManager import BotManager
from libs.ValidationError import ValidationError
from tornado.options import options


class Team(DatabaseObject):

    ''' Team definition '''

    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    _name = Column(Unicode(24), unique=True, nullable=False)
    _motto = Column(Unicode(32))
    files = relationship("FileUpload", backref=backref("team", lazy="select"))
    pastes = relationship("PasteBin", backref=backref("team", lazy="select"))
    money = Column(Integer, default=500, nullable=False)

    members = relationship("User",
                           backref=backref("team", lazy="select")
                           )

    flags = relationship("Flag",
                         secondary=team_to_flag,
                         backref=backref("team", lazy="select")
                         )

    boxes = relationship("Box",
                         secondary=team_to_box,
                         backref=backref("team", lazy="select")
                         )

    items = relationship("MarketItem",
                         secondary=team_to_item,
                         backref=backref("team", lazy="joined")
                         )

    purchased_source_code = relationship("SourceCode",
                                         secondary=team_to_source_code,
                                         backref=backref("team", lazy="select")
                                         )

    hints = relationship("Hint",
                         secondary=team_to_hint,
                         backref=backref("team", lazy="select")
                         )

    game_levels = relationship("GameLevel",
                               secondary=team_to_game_level,
                               backref=backref("team", lazy="select")
                               )

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_name(cls, name):
        ''' Return the team object based on "team_name" '''
        return dbsession.query(cls).filter_by(_name=unicode(name)).first()

    @classmethod
    def ranks(cls):
        ''' Returns a list of all objects in the database '''
        return sorted(dbsession.query(cls).all())

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not 3 <= len(value) <= 24:
            raise ValidationError("Team name must be 3 - 24 characters")
        else:
            self._name = unicode(value)

    @property
    def motto(self):
        return self._motto

    @motto.setter
    def motto(self, value):
        if 32 < len(value):
            raise ValidationError("Motto must be less than 32 characters")
        else:
            self._motto = unicode(value)

    @property
    def levels(self):
        ''' Sorted game_levels '''
        return sorted(self.game_levels)

    def level_flags(self, lvl):
        ''' Given a level number return all flags captured for that level '''
        return filter(lambda flag: flag.game_level.number == lvl, self.flags)

    @property
    def bot_count(self):
        bot_manager = BotManager.instance()
        return bot_manager.count_by_team_uuid(self.uuid)

    def file_by_file_name(self, file_name):
        ''' Return file object based on file_name '''
        ls = self.files.filter_by(file_name=file_name)
        return ls[0] if 0 < len(ls) else None

    def to_dict(self):
        ''' Use for JSON related tasks; return public data only '''
        return {
            'uuid': self.uuid,
            'name': self.name,
            'motto': self.motto,
            'money': self.money,
        }

    def to_xml(self, parent):
        team_elem = ET.SubElement(parent, "team")
        ET.SubElement(team_elem, "name").text = self.name
        ET.SubElement(team_elem, "motto").text = self.motto
        users_elem = ET.SubElement(team_elem, "users")
        users_elem.set("count", str(len(self.members)))
        for user in self.members:
            user.to_xml(users_elem)

    def __repr__(self):
        return u'<Team - name: %s, money: %d>' % (self.name, self.money)

    def __str__(self):
        return self.name.encode('ascii', 'ignore')

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        ''' Compare based on the config option rank_by '''
        if options.rank_by.lower() != 'money':
            this, that = len(self.flags), len(other.flags)
        else:
            this, that = self.money, other.money
        if this < that:
            return 1
        elif this == that:
            return 0
        else:
            return -1
