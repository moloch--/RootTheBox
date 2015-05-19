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


import os
import imghdr
import xml.etree.cElementTree as ET

from uuid import uuid4
from hashlib import md5, sha1, sha256, sha512
from pbkdf2 import PBKDF2
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, String, Boolean, DateTime
from models import dbsession
from models.Team import Team
from models.Permission import Permission
from models.MarketItem import MarketItem
from models.BaseModels import DatabaseObject
from libs.XSSImageCheck import is_xss_image
from libs.ValidationError import ValidationError
from string import printable
from tornado.options import options



# Constants
ADMIN_PERMISSION = u'admin'
DEFAULT_HASH_ALGORITHM = 'md5'
ITERATE = 0x2bad  # 11181
IMG_FORMATS = ['png', 'jpeg', 'gif', 'bmp']
MAX_AVATAR_SIZE = 1024 * 1024
MIN_AVATAR_SIZE = 64


class User(DatabaseObject):

    ''' User definition '''

    uuid = Column(String(36),
                  unique=True,
                  nullable=False,
                  default=lambda: str(uuid4())
                  )

    team_id = Column(Integer, ForeignKey('team.id'))
    _avatar = Column(String(64))
    _locked = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime)
    logins = Column(Integer, default=0)
    _handle = Column(Unicode(16), unique=True, nullable=False)
    _password = Column('password', String(64))
    _bank_password = Column('bank_password', String(128))

    theme_id = Column(Integer, ForeignKey('theme.id'),
                      default=3,
                      nullable=False
                      )

    algorithm = Column(String(8),
                       default=DEFAULT_HASH_ALGORITHM,
                       nullable=False
                       )

    permissions = relationship("Permission",
                               backref=backref("user", lazy="select"),
                               cascade="all,delete,delete-orphan"
                               )
    notifications = relationship("Notification",
                                 backref=backref("user", lazy="select"),
                                 cascade="all,delete,delete-orphan"
                                 )

    algorithms = {
        'md5': (md5, 1, 'md5',),
        'sha1': (sha1, 2, 'sha1',),
        'sha256': (sha256, 3, 'sha256',),
        'sha512': (sha512, 4, 'sha512',),
    }

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def all_users(cls):
        ''' Return all non-admin user objects '''
        return filter(
            lambda user: user.has_permission(
                ADMIN_PERMISSION) is False, cls.all()
        )

    @classmethod
    def not_team(cls, tid):
        ''' Return all users not on a given team, exclude admins '''
        teams = dbsession.query(cls).filter(cls.team_id != tid).all()
        return filter(
            lambda user: user.has_permission(ADMIN_PERMISSION) is False, teams
        )

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(_uuid)).first()

    @classmethod
    def by_handle(cls, handle):
        ''' Return the user object whose user is "_handle" '''
        return dbsession.query(cls).filter_by(_handle=unicode(handle)).first()

    @classmethod
    def _hash_bank_password(cls, algorithm_name, password):
        '''
        Hashes the password using Md5/Sha1/Sha256/Sha512
        only used for the admin accounts.  We only allow
        whitespace/non-ascii.
        '''
        if algorithm_name is None:
            algorithm_name = DEFAULT_HASH_ALGORITHM
        if algorithm_name in cls.algorithms:
            algo = cls.algorithms[algorithm_name][0]()
            algo.update(password)
            return algo.hexdigest()
        else:
            raise ValueError("Algorithm %s not supported." % algorithm_name)

    @classmethod
    def _hash_password(cls, password):
        return PBKDF2.crypt(password, iterations=ITERATE)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        _password = filter(lambda char: char in printable[:-6], value)
        if len(_password) >= options.min_user_password_length:
            self._password = self._hash_password(value)
        else:
            raise ValidationError("Invalid password length (min %d chars)" % (
                options.min_user_password_length,
            ))

    @property
    def bank_password(self):
        return self._bank_password

    @bank_password.setter
    def bank_password(self, value):
        _password = filter(lambda char: char in printable[:-6], value)
        if 0 < len(_password) <= options.max_password_length:
            self._bank_password = self._hash_bank_password(self.algorithm, _password)
        else:
            raise ValidationError("Invalid bank password length (max %d chars)" % (
                options.max_password_length,
            ))

    @property
    def handle(self):
        return self._handle

    @handle.setter
    def handle(self, new_handle):
        if not 3 <= len(new_handle) <= 16:
            raise ValidationError("Handle must be 3 - 16 characters")
        self._handle = unicode(new_handle)

    @property
    def permissions(self):
        ''' Return a set with all permissions granted to the user '''
        return dbsession.query(Permission).filter_by(user_id=self.id)

    @property
    def permissions_names(self):
        ''' Return a list with all permissions accounts granted to the user '''
        return [permission.name for permission in self.permissions]

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

    @property
    def avatar(self):
        if self._avatar is not None:
            return self._avatar
        else:
            return "default_avatar.jpeg"

    @avatar.setter
    def avatar(self, image_data):
        if MIN_AVATAR_SIZE < len(image_data) < MAX_AVATAR_SIZE:
            ext = imghdr.what("", h=image_data)
            if ext in IMG_FORMATS and not is_xss_image(image_data):
                if self._avatar is not None and os.path.exists(options.avatar_dir + '/' + self._avatar):
                    os.unlink(options.avatar_dir + '/' + self._avatar)
                file_path = str(options.avatar_dir + '/' + self.uuid + '.' + ext)
                with open(file_path, 'wb') as fp:
                    fp.write(image_data)
                self._avatar = self.uuid + '.' + ext
            else:
                raise ValidationError("Invalid image format, avatar must be: %s" % (
                    ' '.join(IMG_FORMATS)
                ))
        else:
            raise ValidationError("The image is too large must be %d - %d bytes"  % (
                MIN_AVATAR_SIZE, MAX_AVATAR_SIZE
            ))

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
            return self.password == PBKDF2.crypt(attempt, self.password)
        else:
            return False

    def validate_bank_password(self, attempt):
        ''' Check the bank password against existing credentials '''
        if self._bank_password is not None:
            result = self._hash_bank_password(self.algorithm, attempt)
            return self.bank_password == result
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
        return self.notifications.sort(
            key=lambda notify: notify.created)[:limit]

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
        return {
            'uuid': self.uuid,
            'handle': self.handle,
            'hash_algorithm': self.algorithm,
            'team_uuid': self.team.uuid,
        }

    def to_xml(self, parent):
        '''
        Admins cannot be exported as XML, not that they would be
        exported because they're not on a team, but check anyways
        '''
        if not self.has_permission(ADMIN_PERMISSION):
            user_elem = ET.SubElement(parent, "user")
            ET.SubElement(user_elem, "handle").text = self.handle
            ET.SubElement(user_elem, "password").text = self._password
            bpass_elem = ET.SubElement(user_elem, "bankpassword")
            bpass_elem.text = self._bank_password
            bpass_elem.set("algorithm", self.algorithm)
            with open(options.avatar_dir + self.avatar) as fp:
                data = fp.read()
                ET.SubElement(user_elem, "avatar").text = data.encode('base64')

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return self.handle

    def __repr__(self):
        return u'<User - handle: %s>' % (self.handle,)
