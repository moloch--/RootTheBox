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
from sqlalchemy import Column #ForeignKey
from sqlalchemy.orm import relationship, backref, synonym
from sqlalchemy.types import Integer, Unicode
from models import dbsession, team_to_box, team_to_item, \
    team_to_flag, team_to_game_level
from models.BaseGameObject import BaseObject
from string import ascii_letters, digits


class Team(BaseObject):
    ''' Team definition '''

    _name = Column(Unicode(64), unique=True, nullable=False)
    name = synonym('_name', descriptor=property(
        lambda self: self._name,
        lambda self, name: setattr(
            self, '_name', self.__class__.filter_string(name, " -_"))
    ))
    motto = Column(Unicode(255))
    members = relationship("User", backref=backref("Team", lazy="joined"), cascade="all, delete-orphan")
    listen_port = Column(Integer, default=lambda: randint(1024, 65535), unique=True, nullable=False)
    files = relationship("FileUpload", backref=backref("Team", lazy="dynamic"))
    pastes = relationship("PasteBin", backref=backref("Team", lazy="dynamic"))
    money = Column(Integer, default=0, nullable=False)
    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    flags = relationship("Flag", secondary=team_to_flag, backref="Team")
    boxes = relationship("Box", secondary=team_to_box, backref="Team")
    items = relationship("MarketItem", secondary=team_to_item, backref="Team")
    game_levels = relationship("GameLevel", secondary=team_to_game_level, backref="Team")

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, identifier):
        ''' Returns a the object with id of identifier '''
        return dbsession.query(cls).filter_by(id=identifier).first()

    @classmethod
    def by_name(cls, team_name):
        ''' Return the team object based on "team_name" '''
        return dbsession.query(cls).filter_by(name=unicode(team_name)).first()

    @classmethod
    def by_team_id(cls, team_id):
        ''' Return the team object based one id '''
        return dbsession.query(cls).filter_by(id=team_id).first()

    @classmethod
    def by_uuid(cls, team_uuid):
        ''' Return the job object whose user uuid is "team_uuid" '''
        return dbsession.query(cls).filter_by(uuid=unicode(team_uuid)).first()

    @classmethod
    def filter_string(cls, string, extra_chars=''):
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    def file_by_file_name(self, file_name):
        ''' Return file object based on file_name '''
        return self.files.filter_by(file_name=file_name).first()

    def file_by_uuid(self, uuid):
        ''' Return file object based on uuid '''
        return self.files.filter_by(uuid=uuid).first()

    def __repr__(self):
        return u'<Team - name: %s, money: %d>' % (self.name, self.money)

    def __str__(self):
        return unicode(self.name)
