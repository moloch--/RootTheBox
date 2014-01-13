# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2012

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
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.types import Integer, Unicode, String
from models import dbsession
from models.BaseGameObject import BaseObject
from tornado import netutil


class IpAddress(BaseObject):
    ''' IP Address definition '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)
    _v4 = Column(Unicode(16), unique=True)
    v4 = synonym('_v4', descriptor=property(
        lambda self: self._v4,
        lambda self, v4: setattr(
            self, '_v4', self.__class__.validate_ip(v4))
    ))
    _v6 = Column(Unicode(40), unique=True)
    v6 = synonym('_v6', descriptor=property(
        lambda self: self._v6,
        lambda self, v6: setattr(
            self, '_v6', self.__class__.validate_ip(v6))
    ))

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, identifier):
        ''' Returns a the object with id of identifier '''
        return dbsession.query(cls).filter_by(id=identifier).first()

    @classmethod
    def by_uuid(cls, uuid):
        ''' Return and object based on a uuid '''
        return dbsession.query(cls).filter_by(uuid=unicode(uuid)).first()

    @classmethod
    def by_address(cls, addr):
        ''' Return and object based on an address '''
        ip = dbsession.query(cls).filter_by(v4=unicode(addr)).first()
        if ip is None:
            ip = dbsession.query(cls).filter_by(v6=unicode(addr)).first()
        return ip

    @classmethod
    def validate_ip(cls, ip_address):
        ''' Checks the format of the string to confirm its a valid IPv4 or v6 address '''
        if netutil.is_valid_ip(ip_address):
            return ip_address
        else:
            raise ValueError("Invalid IP Address: '%s'" % str(ip_address))

    def is_v4(self):
        return bool(self.v4 is not None)

    def is_v6(self):
        return bool(self.v6 is not None)

    def __repr__(self):
        return "<IpAddress - v4: %s, v6: %s>" % (str(self.v4), str(self.v6))

    def __str__(self):
        if self.v6 is not None:
            return self.v6
        else:
            return self.v4

    def __eq__(self, other):
        if self.v6 is not None:
            return self.v6 == other.v6
        else:
            return self.v4 == other.v4
