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


import os
import imghdr
import xml.etree.cElementTree as ET

from os import urandom
from uuid import uuid4
from libs.ConfigManager import ConfigManager
from sqlalchemy import Column, ForeignKey, or_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode, String, Boolean
from models import dbsession
from models.BaseModels import DatabaseObject
from models.Relationships import team_to_box
from models.IpAddress import IpAddress
from models.GameLevel import GameLevel
from models.Corporation import Corporation
from models.SourceCode import SourceCode
from models.Hint import Hint


class Box(DatabaseObject):
    ''' Box definition '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    corporation_id = Column(Integer, ForeignKey('corporation.id'), nullable=False)
    _name = Column(Unicode(16), unique=True, nullable=False)
    _operating_system = Column(Unicode(16))
    _description = Column(Unicode(1024))
    _difficulty = Column(Unicode(16))
    game_level_id = Column(Integer, ForeignKey('game_level.id'), nullable=False)
    _avatar = Column(String(64))
    autoformat = Column(Boolean, default=True)

    garbage = Column(String(32),
        unique=True,
        nullable=False,
        default=lambda: urandom(16).encode('hex')
    )

    teams = relationship("Team",
        secondary=team_to_box,
        backref=backref("box", lazy="select")
    )

    hints = relationship("Hint",
        backref=backref("box", lazy="select"),
        cascade="all,delete,delete-orphan"
    )

    flags = relationship("Flag",
        backref=backref("box", lazy="select"),
        cascade="all,delete,delete-orphan"
    )

    ip_addresses = relationship("IpAddress",
        backref=backref("box", lazy="select"),
        cascade="all,delete,delete-orphan"
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
        return dbsession.query(cls).filter_by(uuid=unicode(_uuid)).first()

    @classmethod
    def by_name(cls, name):
        ''' Return the box object whose name is "name" '''
        return dbsession.query(cls).filter_by(_name=unicode(name)).first()

    @classmethod
    def by_garbage(cls, _garbage):
        return dbsession.query(cls).filter_by(garbage=_garbage).first()

    @classmethod
    def by_ip_address(cls, ip_addr):
        '''
        Returns a box object based on an ip address, supports both ipv4
        and ipv6
        '''
        ip = dbsession.query(IpAddress).by_address(ip_addr).first()
        return ip.box if ip is not None else None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not 3 < len(value) < 16:
            raise ValueError("Name must be 3 - 16 characters")
        self._name = unicode(value)

    @property
    def operating_system(self):
        return self._operating_system if self._operating_system else '?'

    @operating_system.setter
    def operating_system(self, value):
        self._operating_system = unicode(value)

    @property
    def description(self):
        '''
        We have to ensure that the description text is formatted correctly,
        it gets dumped into a <pre> tag which will honor whitespace this will
        split all of the text and insert newlines every 70 chars +2 whitespace
        at be beginning of each line, so the indents line up nicely.
        '''
        if self.autoformat:
            index, step = 0, 70
            ls = [' ']
            if 0 < len(self._description):
                text = self._description.replace('\n', '')
                while index < len(text):
                    ls.append("  " + text[index: index + step])
                    index += step
            else:
                ls.append("  No information on file.")
            ls.append("\n  Operating System: %s\n" % self.operating_system)
            ls.append("  Reported Difficulty: %s\n" % self.difficulty)
            return unicode("\n".join(ls))
        else:
            return self._description

    @description.setter
    def description(self, value):
        if 1024 < len(value):
            raise ValueError("Description must be less than 1024 characters")
        self._description = unicode(value)

    @property
    def difficulty(self):
        return self._difficulty if len(self._difficulty) else u"Unknown"

    @difficulty.setter
    def difficulty(self, value):
        if 16 < len(value):
            raise ValueError("Difficulty must be less than 16 characters")
        self._difficulty = unicode(value)

    @property
    def avatar(self):
        if self._avatar is not None:
            return self._avatar
        else:
            return "default_avatar.jpeg"

    @avatar.setter
    def avatar(self, image_data):
        if self.uuid is None:
            self.uuid = str(uuid4())
        if len(image_data) < (1024 * 1024):
            ext = imghdr.what("", h=image_data)
            if ext in ['png', 'jpeg', 'gif', 'bmp']:
                config = ConfigManager.instance()
                if self._avatar is not None and os.path.exists(config.avatar_dir + self._avatar):
                    os.unlink(config.avatar_dir + self._avatar)
                file_path = str(config.avatar_dir + self.uuid + '.' + ext)
                with open(file_path, 'wb') as fp:
                    fp.write(image_data)
                self._avatar = self.uuid + '.' + ext
            else:
                raise ValueError("Invalid image format, avatar must be: .png .jpeg .gif or .bmp")
        else:
            raise ValueError("The image is too large")

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

    @property
    def source_code(self):
        return SourceCode.by_box_id(self.id)

    def get_garbage_cfg(self):
        return "[Bot]\nname = %s\ngarbage = %s\n" % (
            self.name.encode('hex'), self.garbage
        )

    def to_xml(self, parent):
        ''' Convert object to XML '''
        box_elem = ET.SubElement(parent, "box")
        box_elem.set("gamelevel", str(self.game_level.number))
        ET.SubElement(box_elem, "name").text = self.name
        ET.SubElement(box_elem, "operatingsystem").text = self._operating_system
        ET.SubElement(box_elem, "description").text = self._description
        ET.SubElement(box_elem, "difficulty").text = self._difficulty
        ET.SubElement(box_elem, "garbage").text = self.garbage
        flags_elem = ET.SubElement(box_elem, "flags")
        flags_elem.set("count", str(len(self.flags)))
        for flag in self.flags:
            flag.to_xml(flags_elem)
        hints_elem = ET.SubElement(box_elem, "hints")
        hints_elem.set("count", str(len(self.hints)))
        for hint in self.hints:
            hint.to_xml(hints_elem)
        ips_elem = ET.SubElement(box_elem, "ipaddresses")
        ips_elem.set("count", str(len(self.ips)))
        for ip in self.ips:
            ip.to_xml(ips_elem)
        config = ConfigManager.instance()
        with open(config.avatar_dir + self.avatar) as favatar:
            data = favatar.read()
            ET.SubElement(box_elem, "avatar").text = data.encode('base64')

    def to_dict(self):
        ''' Returns editable data as a dictionary '''
        corp = Corporation.by_id(self.corporation_id)
        game_level = GameLevel.by_id(self.game_level_id)
        return {
            'name': self.name,
            'uuid': self.uuid,
            'corporation': corp.uuid,
            'description': self._description,
            'difficulty': self.difficulty,
            'game_level': game_level.uuid,
        }

    def __repr__(self):
        return u'<Box - name: %s>' % (self.box_name,)

    def __str__(self):
        return self.box_name
