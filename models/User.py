# -*- coding: utf-8 -*-
"""
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

This file contains the user object, used to store data related to an
indiviudal user, such as handle/account/password/etc

"""


import os
import imghdr
import string
import random
import io
import xml.etree.cElementTree as ET
from uuid import uuid4
from datetime import datetime
from hashlib import md5, sha1, sha256, sha512
from pbkdf2 import PBKDF2
from sqlalchemy import Column, ForeignKey, desc, func
from sqlalchemy.orm import synonym, relationship, backref
from sqlalchemy.types import Unicode, Integer, String, Boolean, DateTime
from models import dbsession
from models.Permission import Permission
from models.MarketItem import MarketItem
from models.BaseModels import DatabaseObject
from models.EmailToken import EmailToken
from models.Theme import Theme
from models.Relationships import user_to_flag
from libs.XSSImageCheck import MAX_AVATAR_SIZE, MIN_AVATAR_SIZE, IMG_FORMATS
from libs.XSSImageCheck import is_xss_image, get_new_avatar, default_avatar
from libs.ValidationError import ValidationError
from libs.WebhookHelpers import send_user_validated_webhook
from string import printable
from tornado.options import options
from PIL import Image
from resizeimage import resizeimage
from libs.StringCoding import encode
from builtins import str
from past.builtins import basestring


# Constants
ADMIN_PERMISSION = "admin"
DEFAULT_HASH_ALGORITHM = "md5"
ITERATE = 0x2BAD  # 11181


class User(DatabaseObject):

    """User definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    team_id = Column(Integer, ForeignKey("team.id"))
    _avatar = Column(String(64))
    _locked = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime)
    logins = Column(Integer, default=0)
    _handle = Column(Unicode(16), unique=True, nullable=False)
    _name = Column(Unicode(64), unique=False, nullable=True)
    _email = Column(Unicode(64), unique=False, nullable=True)
    _password = Column("password", String(64))
    _bank_password = Column("bank_password", String(128))
    _notes = Column(Unicode(512))
    _expire = Column(DateTime, default=None, nullable=True)
    money = Column(Integer, default=0, nullable=False)

    theme_id = Column(Integer, ForeignKey("theme.id"), default=3, nullable=False)

    algorithm = Column(String(8), default=DEFAULT_HASH_ALGORITHM, nullable=False)

    permissions = relationship(
        "Permission",
        backref=backref("user", lazy="select"),
        cascade="all,delete,delete-orphan",
    )
    notifications = relationship(
        "Notification",
        backref=backref("user", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    algorithms = {
        "md5": (md5, 1, "md5"),
        "sha1": (sha1, 2, "sha1"),
        "sha256": (sha256, 3, "sha256"),
        "sha512": (sha512, 4, "sha512"),
    }

    flags = relationship(
        "Flag", secondary=user_to_flag, backref=backref("user", lazy="select")
    )

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def all_users(cls):
        """Return all non-admin user objects"""
        return [user for user in cls.all() if user.is_admin() is False]

    @classmethod
    def not_team(cls, tid):
        """Return all users not on a given team, exclude admins"""
        teams = dbsession.query(cls).filter(cls.team_id != tid).all()
        return [user for user in teams if user.is_admin() is False]

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def by_email(cls, email):
        """Return an object based on a email"""
        if email and len(email) > 0:
            return (
                dbsession.query(cls)
                .filter(func.lower(User._email) == func.lower(email))
                .first()
            )
        else:
            return None

    @classmethod
    def by_handle(cls, handle):
        """Return the user object whose user is "_handle" """
        if handle and len(handle) > 0:
            handle = str(handle).strip()
            return (
                dbsession.query(cls)
                .filter(func.lower(User._handle) == func.lower(handle))
                .first()
            )
        else:
            return None

    @classmethod
    def _hash_bank_password(cls, algorithm_name, password):
        """
        Hashes the password using Md5/Sha1/Sha256/Sha512
        only used for the admin accounts.  We only allow
        whitespace/non-ascii.
        """
        if algorithm_name is None:
            algorithm_name = DEFAULT_HASH_ALGORITHM
        if algorithm_name in cls.algorithms:
            algo = cls.algorithms[algorithm_name][0]()
            algo.update(encode(password))
            return algo.hexdigest()
        else:
            raise ValueError("Algorithm %s not supported." % algorithm_name)

    @classmethod
    def _hash_password(cls, password):
        return PBKDF2.crypt(password, iterations=ITERATE)

    @classmethod
    def ranks(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).filter_by(_locked=0).order_by(desc(cls.money)).all()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        _password = "".join([char for char in value if char in printable[:-6]])
        if len(_password) >= int(options.min_user_password_length):
            self._password = self._hash_password(value)
        else:
            raise ValidationError(
                "Invalid password length (min %d chars)"
                % (options.min_user_password_length,)
            )

    @property
    def theme(self):
        if self.theme_id:
            return Theme.by_id(self.theme_id).name
        else:
            return options.default_theme

    @theme.setter
    def theme(self, value):
        theme = Theme.by_name(value)
        if theme:
            self.theme_id = theme.id

    @property
    def bank_password(self):
        return self._bank_password

    @bank_password.setter
    def bank_password(self, value):
        if not options.banking or not value:
            # random password
            _password = "".join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(options.max_password_length)
            )
        else:
            _password = "".join([char for char in value if char in printable[:-6]])
        if 0 < len(_password) <= options.max_password_length:
            self._bank_password = self._hash_bank_password(self.algorithm, _password)
        else:
            raise ValidationError(
                "Invalid bank password length (max %d chars)"
                % (options.max_password_length,)
            )

    @property
    def handle(self):
        return self._handle

    @handle.setter
    def handle(self, new_handle):
        new_handle = str(new_handle).strip()
        if not 3 <= len(new_handle) <= 16:
            raise ValidationError("Handle must be 3 - 16 characters")
        self._handle = new_handle

    @property
    def expire(self):
        if self._expire is None or self._expire == "":
            return ""
        return self._expire.strftime("%m/%d/%Y")

    @expire.setter
    def expire(self, expire):
        if expire and len(expire) > 0 and not self.is_admin():
            self._expire = datetime.strptime(expire, "%m/%d/%Y")
        else:
            self._expire = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if len(new_name) > 64:
            raise ValidationError("Name must be 0 - 64 characters")
        self._name = str(new_name)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        if len(new_email) > 64:
            raise ValidationError("Email must be 0 - 64 characters")
        self._email = str(new_email)

    @property
    def notes(self):
        if self._notes is None:
            self._notes = ""
        return self._notes

    @notes.setter
    def notes(self, new_notes):
        if len(new_notes) > 512:
            raise ValidationError("Notes must be 0 - 512 characters")
        self._notes = str(new_notes)

    @property
    def permissions_all(self):
        """Return a set with all permissions granted to the user"""
        return dbsession.query(Permission).filter_by(user_id=self.id)

    @property
    def permissions_names(self):
        """Return a list with all permissions accounts granted to the user"""
        return [permission.name for permission in self.permissions_all]

    @property
    def locked(self):
        """
        Determines if an admin has locked an account, accounts with
        administrative permissions cannot be locked.
        """
        if self.is_admin():
            return False  # Admin accounts cannot be locked
        else:
            return self._locked

    @locked.setter
    def locked(self, value):
        """Setter method for _lock"""
        assert isinstance(value, bool)
        if not self.is_admin():
            self._locked = value
            if not self._locked:
                # admin email validation
                emailtoken = EmailToken.by_user_id(self.id)
                if emailtoken and not emailtoken.valid:
                    emailtoken.valid = True
                    dbsession.add(emailtoken)
                    dbsession.commit()
                    send_user_validated_webhook(self)

    @property
    def avatar(self):
        if self._avatar is not None:
            return self._avatar
        else:
            if not options.teams:
                avatar = default_avatar("user")
            elif self.is_admin():
                avatar = default_avatar("user")
            else:
                avatar = get_new_avatar("user")
                if not avatar.startswith("default_"):
                    self._avatar = avatar
                    dbsession.add(self)
                    dbsession.commit()
            return avatar

    @avatar.setter
    def avatar(self, image_data):
        if MIN_AVATAR_SIZE < len(image_data) < MAX_AVATAR_SIZE:
            ext = imghdr.what("", h=image_data)
            if ext in IMG_FORMATS and not is_xss_image(image_data):
                try:
                    if self._avatar is not None and os.path.exists(
                        options.avatar_dir + "/upload/" + self._avatar
                    ):
                        os.unlink(options.avatar_dir + "/upload/" + self._avatar)
                    file_path = str(
                        options.avatar_dir + "/upload/" + self.uuid + "." + ext
                    )
                    image = Image.open(io.BytesIO(image_data))
                    cover = resizeimage.resize_cover(image, [500, 250])
                    cover.save(file_path, image.format)
                    self._avatar = "upload/" + self.uuid + "." + ext
                except Exception as e:
                    raise ValidationError(e)
            else:
                raise ValidationError(
                    "Invalid image format, avatar must be: %s"
                    % (", ".join(IMG_FORMATS))
                )
        else:
            raise ValidationError(
                "The image is too large must be %d - %d bytes"
                % (MIN_AVATAR_SIZE, MAX_AVATAR_SIZE)
            )

    def has_item(self, item_name):
        """Check to see if a team has purchased an item"""
        item = MarketItem.by_name(item_name)
        if item is None:
            raise ValueError("Item '%s' not in database." % str(item_name))
        return True if self.team and item in self.team.items else False

    def has_permission(self, permission):
        """Return True if 'permission' is in permissions_names"""
        return True if permission in self.permissions_names else False

    def is_admin(self):
        return self.has_permission(ADMIN_PERMISSION)

    def is_email_valid(self):
        emailtoken = EmailToken.by_user_id(self.id)
        if emailtoken is None:
            return True
        return emailtoken.valid

    def is_expired(self):
        expired = self._expire
        if expired and expired != "":
            return datetime.now() > expired
        return False

    def validate_email(self, token):
        emailtoken = EmailToken.by_user_id(self.id)
        if emailtoken and emailtoken.value == token:
            emailtoken.valid = True
            dbsession.add(emailtoken)
            dbsession.commit()
        return self.is_email_valid()

    def validate_password(self, attempt):
        """Check the password against existing credentials"""
        if self._password is not None:
            return self.password == PBKDF2.crypt(attempt, self.password)
        else:
            return False

    def validate_bank_password(self, attempt):
        """Check the bank password against existing credentials"""
        if self._bank_password is not None:
            result = self._hash_bank_password(self.algorithm, attempt)
            return self.bank_password == result
        else:
            return False

    def get_new_notifications(self):
        """
        Returns any unread messages

        @return: List of unread messages
        @rtype: List of Notification objects
        """
        return [notify for notify in self.notifications if notify.viewed is False]

    def get_notifications(self, limit=10):
        """
        Returns most recent notifications

        @param limit: Max number of notifications to return, defaults to 10
        @return: Most recent notifications
        @rtype: List of Notification objects
        """
        return self.notifications.sort(key=lambda notify: notify.created)[:limit]

    def next_algorithm(self):
        """Returns next algo"""
        current = self.get_algorithm(self.algorithm)
        return self.get_algorithm(current[1] + 1)

    def get_algorithm(self, index):
        """Return algorithm tuple based on string or int"""
        if isinstance(index, basestring) and index in self.algorithms:
            return self.algorithms[index]
        elif isinstance(index, int):  # Find by numeric index
            for key in self.algorithms:
                if index == self.algorithms[key][1]:
                    return self.algorithms[key]
        return None

    def to_dict(self):
        """Return user data as dictionary"""
        return {
            "uuid": self.uuid,
            "handle": self.handle,
            "name": self.name,
            "email": self.email,
            "admin": str(self.is_admin()).lower(),
            "hash_algorithm": self.algorithm,
            "team_uuid": self.team.uuid if self.team else "",
            "avatar": self.avatar,
            "notes": self.notes,
            "expire": self.expire,
        }

    def to_xml(self, parent):
        """
        Admins cannot be exported as XML, not that they would be
        exported because they're not on a team, but check anyways
        """
        if not self.is_admin():
            user_elem = ET.SubElement(parent, "user")
            ET.SubElement(user_elem, "handle").text = self.handle
            ET.SubElement(user_elem, "name").text = self.name
            ET.SubElement(user_elem, "email").text = self.email
            ET.SubElement(user_elem, "password").text = self._password
            ET.SubElement(user_elem, "notes").text = self.notes
            ET.SubElement(user_elem, "expire").text = self.expire
            bpass_elem = ET.SubElement(user_elem, "bankpassword")
            bpass_elem.text = self._bank_password
            bpass_elem.set("algorithm", self.algorithm)
            with open(options.avatar_dir + self.avatar) as fp:
                data = fp.read()
                ET.SubElement(user_elem, "avatar").text = encode(data, "base64")

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.handle

    def __repr__(self):
        return "<User - handle: %s>" % (self.handle,)
