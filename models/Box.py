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
from sqlalchemy import Column, ForeignKey, or_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode
from models import dbsession, team_to_box, IpAddress
from models.BaseGameObject import BaseObject


class Box(BaseObject):
    ''' Box definition '''

    uuid = Column(Unicode(36), unique=True, nullable=False, default=lambda: unicode(uuid4()))
    corporation_id = Column(Integer, ForeignKey('corporation.id'), nullable=False)
    name = Column(Unicode(64), unique=True, nullable=False)
    ip_addresses = relationship("IpAddress", backref=backref("Box", lazy="joined"), cascade="all, delete-orphan")
    description = Column(Unicode(2048))
    difficulty = Column(Unicode(64), nullable=False)
    game_level_id = Column(Integer, ForeignKey('game_level.id'), nullable=False)
    teams = relationship("Team", secondary=team_to_box, backref=backref("Box", lazy="joined"))
    flags = relationship("Flag", backref=backref("Box", lazy="joined"), cascade="all, delete-orphan")

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
    def by_name(cls, name):
        ''' Return the box object whose name is "name" '''
        return dbsession.query(cls).filter_by(name=unicode(name)).first()

    @classmethod
    def by_ip_address(cls, ip_address):
        ''' Returns a box object based on an ip address, supports both ipv4 and ipv6 '''
        ip = dbsession.query(IpAddress).filter(or_(IpAddress.v4 == ip_address, IpAddress.v6 == ip_address)).first()
        if ip is not None:
            return dbsession.query(cls).filter_by(id=ip.box_id).first()
        else:
            return None

    @property
    def ips(self):
        ''' Return all ip addresses '''
        return self.ipv4 + self.ipv6

    @property
    def ipv4(self):
        ''' Return a list of all ipv4 addresses '''
        ips = [ip.v4 for ip in self.ip_addresses]
        return filter(lambda ip: ip is not None, ips)

    @property
    def ipv6(self):
        ''' Return a list of all ipv6 addresses '''
        ips = [ip.v6 for ip in self.ip_addresses]
        return filter(lambda ip: ip is not None, ips)

    def to_dict(self):
        ''' Returns editable data as a dictionary '''
        return dict(
            name=self.name, 
            corporation_id=self.corporation_id,
            description=self.description,
            difficulty=self.difficulty,
            game_level_id=self.game_level_id,
        )

    def __repr__(self):
        return u'<Box - name: %s>' % (self.box_name,)

    def __str__(self):
        return self.box_name.encode('ascii', 'ignore')

    def __unicode__(self):
        return self.box_name