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
"""

import logging

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy.sql import and_
from sqlalchemy.types import Unicode, String, Integer, Boolean
from models import dbsession
from models.User import User
from models.BaseModels import DatabaseObject
from tornado.options import options
from builtins import str


### Constants ###
SUCCESS = "/static/images/success.png"
INFO = "/static/images/info.png"
WARNING = "/static/images/warning.png"
ERROR = "/static/images/error.png"


class Notification(DatabaseObject):

    """Notification definition"""

    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(Unicode(256), nullable=False)
    message = Column(Unicode(256), nullable=False)
    viewed = Column(Boolean, default=False)
    icon_url = Column(Unicode(256), nullable=True)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).filter_by(user_id=None).all()

    @classmethod
    def admin(cls):
        """Returns a list of unique notifications in the database"""
        return dbsession.query(
            cls.created, cls.icon_url, cls.message, cls.title
        ).distinct()

    @classmethod
    def clear(cls):
        """Deletes all objects in the database"""
        return dbsession.query(cls).delete()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_user_id(cls, _id):
        """Return notifications for a single user"""
        return (
            dbsession.query(cls)
            .filter_by(user_id=_id)
            .order_by(desc(cls.created))
            .all()
        )

    @classmethod
    def unread_by_user_id(cls, user_id):
        """Return all notification which have not been viewed"""
        return (
            dbsession.query(cls)
            .filter(and_(cls.user_id == user_id, cls.viewed == False))
            .all()
        )

    @classmethod
    def create_user(cls, user, title, message, icon=None):
        notification = cls._create(user, title, message, icon)
        dbsession.add(notification)
        dbsession.commit()

    @classmethod
    def create_team(cls, team, title, message, icon=None):
        for user in team.members:
            notification = cls._create(user, title, message, icon)
            dbsession.add(notification)
        dbsession.commit()

    @classmethod
    def create_broadcast(cls, team, title, message, icon=None):
        if not options.global_notification and team:
            cls.create_team(team, title, message, icon)
        else:
            for user in User.all_users():
                notification = cls._create(user, title, message, icon)
                dbsession.add(notification)
            dbsession.commit()

    @classmethod
    def _create(cls, user, title, message, icon=None):
        """Create a notification and save it to the database"""
        logging.debug("Creating notification '%s' for %r" % (title, user))
        icon = icon if icon is not None else INFO
        notification = Notification(
            user_id=user.id,
            title=str(title),
            message=str(message),
            icon_url=urlparse(icon).path,
        )
        return notification

    def to_dict(self):
        """Return public data as dict"""
        return {"title": self.title, "message": self.message, "icon_url": self.icon_url}
