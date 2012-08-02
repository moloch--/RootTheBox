# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

@author: moloch

    Copyright [2012] [Redacted Labs]

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


import string
import logging

from hashlib import md5, sha256
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, Boolean
from models import dbsession, association_table
from models.Box import Box
from models.Team import Team
from models.Post import Post
from models.Action import Action
from models.Permission import Permission
from models.BaseGameObject import BaseObject


class User(BaseObject):
    ''' User definition '''

    name = Column(Unicode(64), unique=True, nullable=False)
    display_name = Column(Unicode(64), unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey('team.id'))
    pastes = relationship("PasteBin", backref=backref("User",
                                                 lazy="joined"), cascade="all, delete-orphan")
    permissions = relationship("Permission", backref=backref("User",
                                                             lazy="joined"), cascade="all, delete-orphan")
    avatar = Column(Unicode(64), default=unicode("default_avatar.jpeg"))
    _password = Column('password', Unicode(128))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(
            self, '_password', self.__class__._hash_password(password))
    ))

    @property
    def permissions(self):
        '''Return a set with all permissions granted to the user.'''
        return dbsession.query(Permission).filter_by(user_id=self.id)

    @property
    def permissions_names(self):
        '''Return a list with all permissions names granted to the user.'''
        return [permission.name for permission in self.permissions]

    @property
    def team_name(self):
        ''' Return a list with all groups names the user is a member of '''
        if self.team_id == None:
            return None
        else:
            team = dbsession.query(
                Team).filter_by(id=self.team_id).first()
            return team.name

    @property
    def team(self):
        ''' Return a the uesr's team object '''
        if self.team_id == None:
            return None
        else:
            return dbsession.query(Team).filter_by(id=self.team_id).first()

    @classmethod
    def get_all(cls):
        ''' Return all non-admin user objects '''
        return dbsession.query(cls).filter(cls.user_name != 'admin').all()

    @classmethod
    def get_free_agents(cls):
        ''' Return all non-admin user objects without a team '''
        return dbsession.query(cls).filter_by(team_id=None).filter(cls.user_name != 'admin').all()

    @classmethod
    def by_user_name(cls, user_name):
        ''' Return the user object whose user name is "user_name" '''
        return dbsession.query(cls).filter_by(name=unicode(user_name)).first()

    @classmethod
    def by_display_name(cls, display_name):
        ''' Return the user object whose user name is "display_name" '''
        return dbsession.query(cls).filter_by(display_name=unicode(display_name)).first()

    @classmethod
    def by_id(cls, user_id):
        ''' Return the user object whose user id is "user_id" '''
        return dbsession.query(cls).filter_by(id=user_id).first()

    @classmethod
    def add_to_team(cls, team_name):
        ''' Add user to team based on team name '''
        team = dbsession.query(Team).filter_by(name=unicode(team_name)).first()
        cls.team_id = team.id

    @classmethod
    def _hash_password(cls, password):
        ''' Hashes the password using Md5/Sha256 :D '''
        password = filter(lambda char: char in string.printable[:-5], password)
        if 8 <= len(password):
            password = cls.admin_hash(password)
        else:
            password = cls.user_hash(password)
        return password

    @classmethod
    def user_hash(cls, preimage):
        ''' Single round md5 '''
        md5_hash = md5()
        md5_hash.update(preimage)
        return unicode(md5_hash.hexdigest())

    @classmethod
    def admin_hash(cls, preimage):
        ''' 25,000 rounds of sha256 '''
        sha_hash = sha256()
        sha_hash.update(preimage)
        for count in range(1, 25000):
            sha_hash.update(preimage + sha_hash.hexdigest() + str(count))
        return unicode(sha_hash.hexdigest())

    def has_permission(self, permission):
        ''' Return True if 'permission' is in permissions_names '''
        return True if permission in self.permissions_names else False

    def validate_password(self, attempt):
        ''' Check the password against existing credentials '''
        attempt = filter(lambda char: char in string.printable[:-5], attempt)
        if isinstance(attempt, unicode):
            attempt = attempt.encode('utf-8')
        if self.has_permission('admin'):
            return self.password == self.admin_hash(attempt)
        else:
            return self.password == self.user_hash(unicode(attempt))

    def give_control(self, box):
        ''' Give team control of a box object '''
        if not self.team.is_controlling(box):
            self.controlled_boxes.append(box)

    def lost_control(self, box):
        ''' Remove team's control over a box object '''
        if box in self.controlled_boxes:
            logging.info("Removed control of %s from %s" % (
                box.box_name, self.display_name))
            self.controlled_boxes.remove(box)

    def __repr__(self):
        return ('<User - name: %s, display: %s, team_id: %d>' % (self.user_name, self.display_name, self.team_id)).encode('utf-8')

    def __radd__(self, other):
        return self.score + other

    def __rsub__(self, other):
        return self.score - other

    def __add__(self, other):
        return self.score + other

    def __sub__(self, other):
        return self.score - other
