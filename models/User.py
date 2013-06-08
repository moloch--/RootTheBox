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
----------------------------------------------------------------------------

This file contiains the user object, used to store data related to an
indiviudal user, such as handle/account/password/etc

'''


from os import urandom
from uuid import uuid4
from hashlib import md5, sha1, sha256
from pbkdf2 import PBKDF2
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, String, Boolean
from models import dbsession, Team, Permission
from models.MarketItem import MarketItem
from models.BaseGameObject import BaseObject
from string import ascii_letters, digits, printable


### Constants
ADMIN_PERMISSION = 'admin'
ADMIN_HASH_ALGORITHM = 'pbkdf2'
DEFAULT_HASH_ALGORITHM = u'md5'
ITERATE = 1337


class User(BaseObject):
    ''' User definition '''

    _account = Column(Unicode(64), unique=True, nullable=False)
    account = synonym('_account', descriptor=property(
        lambda self: self._account,
        lambda self, account: setattr(
            self, '_account', self.__class__.filter_string(account, "_-"))
    ))
    _handle = Column(Unicode(64), unique=True, nullable=False)
    handle = synonym('_handle', descriptor=property(
        lambda self: self._handle,
        lambda self, handle: setattr(
            self, '_handle', self.__class__.filter_string(handle, "_-"))
    ))
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: uuid4())
    _locked = Column(Boolean, default=False, nullable=False)
    team_id = Column(Integer, ForeignKey('team.id'))
    permissions = relationship("Permission", backref=backref("User", lazy="select"), cascade="all, delete-orphan")
    notifications = relationship("Notification", backref=backref("User", lazy="select"), cascade="all, delete-orphan")
    avatar = Column(Unicode(64), default=u"default_avatar.jpeg")
    _password = Column('password', Unicode(128))
    password = synonym('_password', descriptor=property(
        lambda self: self._password,
        lambda self, password: setattr(
            self, '_password', self.__class__._hash_password(self.algorithm, password, self.salt))
    ))
    algorithm = Column(Unicode(8), default=DEFAULT_HASH_ALGORITHM, nullable=False)
    theme_id = Column(Integer, ForeignKey('theme.id'), default=3, nullable=False)
    salt = Column(String(32), default=lambda: urandom(16).encode('hex'))
    algorithms = {
        'md5': (md5, 1, u'md5',), 
        'sha1': (sha1, 2, u'sha1',), 
        'sha256': (sha256, 3, u'sha256',),
    }

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def all_users(cls):
        ''' Return all non-admin user objects '''
        return filter(lambda user: user.has_permission(ADMIN_PERMISSION) is False, cls.all())

    @classmethod
    def by_id(cls, identifier):
        ''' Returns a the object with id of identifier '''
        return dbsession.query(cls).filter_by(id=identifier).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_account(cls, account):
        ''' Return the user object whose user account is "account" '''
        return dbsession.query(cls).filter_by(account=unicode(account)).first()

    @classmethod
    def by_handle(cls, handle):
        ''' Return the user object whose user is "handle" '''
        return dbsession.query(cls).filter_by(handle=unicode(handle)).first()

    @classmethod
    def filter_string(cls, string, extra_chars=''):
        char_white_list = ascii_letters + digits + extra_chars
        return filter(lambda char: char in char_white_list, string)

    @classmethod
    def _hash_password(cls, algorithm_name, password, salt):
        '''
        Hashes the password using Md5/Sha1/Sha256/PBKDF2; pbkdf2 should 
        only used for the admin accounts.

        @param algorithm_name: The hashing algorithm to be used
        @param password: Preimage to be hashed, non-ascii chars are ignored
        @param salt: Salt for password, only used with the pbkdf2 algorithm
        @return: Unicode hexadecimal string of the hash digest
        @rtype: unicode
        '''
        password = filter(lambda char: char in printable[:-5], password)
        password = password.encode('ascii', 'ignore')
        if algorithm_name == ADMIN_HASH_ALGORITHM:
            return cls.__pbkdf2__(password, salt)
        elif algorithm_name in cls.algorithms:
            algo = cls.algorithms[algorithm_name][0]()
            algo.update(password)
            return unicode(algo.hexdigest())
        else:
            raise ValueError("Algorithm not supported.")

    @classmethod
    def __pbkdf2__(cls, password, salt):
        '''
        Uses pbkdf2 to hash the password using a random salt

        @param password: The preimage to be hashed
        @param salt: The auto-generated hash
        @return: Hexadecimal string of the hash digest
        '''
        hashed = PBKDF2(password, salt, iterations=ITERATE).read(32).encode('hex')
        return unicode(hashed)

    @property
    def permissions(self):
        ''' Return a set with all permissions granted to the user '''
        return dbsession.query(Permission).filter_by(user_id=self.id)

    @property
    def permissions_names(self):
        ''' Return a list with all permissions accounts granted to the user '''
        return [permission.name for permission in self.permissions]

    @property
    def team(self):
        ''' Return a the user's team object '''
        return dbsession.query(Team).filter_by(id=self.team_id).first()

    @property
    def locked(self):
        ''' 
        Determines if an admin has locked an account, accounts with
        administrative permissions cannot be locked.
        '''
        if self.has_permission(ADMIN_PERMISSION):
            return False  # Admin accounts cannot be locked
        else:
            return self._locked

    @locked.setter
    def locked(self, value):
        ''' Setter method for _lock '''
        assert isinstance(value, bool)
        if not self.has_permission(ADMIN_PERMISSION):
            self._locked = value

    def has_item(self, item_name):
        ''' Check to see if a team has purchased an item '''
        item = MarketItem.by_name(item_name)
        if item is None:
            raise ValueError("Item '%s' not in database." % str(item_name))
        return True if item in self.team.items else False

    def has_permission(self, permission):
        ''' Return True if 'permission' is in permissions_names '''
        return True if permission in self.permissions_names else False

    def validate_password(self, attempt):
        ''' Check the password against existing credentials '''
        if self._password is not None:
            result = self._hash_password(self.algorithm, attempt, self.salt)
            return self.password == result
        else:
            return False

    def get_new_notifications(self):
        '''
        Returns any unread messages

        @return: List of unread messages
        @rtype: List of Notification objects
        '''
        return filter(
            lambda notify: notify.viewed is False, self.notifications
        )

    def get_notifications(self, limit=10):
        '''
        Returns most recent notifications

        @param limit: Max number of notifications to return, defaults to 10
        @return: Most recent notifications
        @rtype: List of Notification objects
        '''
        return self.notifications.sort(key=lambda notify: notify.created)[:limit]

    def next_algorithm(self):
        ''' Returns next algo '''
        current = self.get_algorithm(self.algorithm)
        return self.get_algorithm(current[1] + 1)

    def get_algorithm(self, index):
        ''' Return algorithm tuple based on string or int '''
        if isinstance(index, basestring) and index in self.algorithms:
            return self.algorithms[index]
        elif isinstance(index, int):  # Find by numeric index
            for key in self.algorithms:
                if index == self.algorithms[key][1]:
                    return self.algorithms[key]
        return None

    def to_dict(self):
        ''' Return public data as dictionary '''
        team = Team.by_id(self.team_id)
        return {
            'uuid': self.uuid,
            'handle': self.handle,
            'account': self.account,
            'hash_algorithm': self.algorithm,
            'team_uuid': team.uuid,
        }

    def __str__(self):
        return self.handle

    def __repr__(self):
        return u'<User - account: %s, handle: %s>' % (self.account, self.handle,)
