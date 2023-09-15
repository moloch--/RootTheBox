# -*- coding: utf-8 -*-
"""
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
"""


import os
import imghdr
import io
import binascii
import xml.etree.cElementTree as ET

from os import urandom
from uuid import uuid4
from collections import OrderedDict
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, Unicode, String, Boolean, Enum
from models import dbsession
from models.BaseModels import DatabaseObject
from models.Relationships import team_to_box
from models.IpAddress import IpAddress
from models.GameLevel import GameLevel
from models.Corporation import Corporation
from models.Category import Category
from models.SourceCode import SourceCode
from tornado.options import options
from libs.XSSImageCheck import is_xss_image, get_new_avatar
from libs.ValidationError import ValidationError
from libs.StringCoding import encode, decode
from PIL import Image
from resizeimage import resizeimage
import enum


class FlagsSubmissionType(str, enum.Enum):
    CLASSIC = "CLASSIC"
    SINGLE_SUBMISSION_BOX = "SINGLE_SUBMISSION_BOX"


from builtins import (  # noqa: E402
    str,
)  # TODO Python2/3 compatibility issue if imported before FlagSubmissionType


class Box(DatabaseObject):
    """Box definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    corporation_id = Column(Integer, ForeignKey("corporation.id"), nullable=False)

    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    _name = Column(Unicode(32), unique=True, nullable=False)
    _operating_system = Column(Unicode(16))
    _description = Column(Unicode(4096))
    _capture_message = Column(Unicode(4096))
    _difficulty = Column(Unicode(16))
    game_level_id = Column(Integer, ForeignKey("game_level.id"), nullable=False)
    _avatar = Column(String(64))
    _value = Column(Integer, nullable=True)
    _locked = Column(Boolean, default=False, nullable=False)
    _order = Column(Integer, nullable=True, index=True)

    garbage = Column(
        String(32),
        unique=True,
        nullable=False,
        default=lambda: binascii.hexlify(urandom(16)).decode(),
    )

    teams = relationship(
        "Team", secondary=team_to_box, back_populates="boxes", lazy="select"
    )

    hints = relationship(
        "Hint",
        backref=backref("box", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    _flags = relationship(
        "Flag",
        backref=backref("box", lazy="select"),
        cascade="all,delete,delete-orphan",
        order_by="desc(-Flag._order)",
    )

    flag_submission_type = Column(
        Enum(FlagsSubmissionType), default=FlagsSubmissionType.CLASSIC
    )

    ip_addresses = relationship(
        "IpAddress",
        backref=backref("box", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return sorted(dbsession.query(cls).all())

    @classmethod
    def unlocked(cls):
        """Return a list of all unlocked objects in the database"""
        return dbsession.query(cls).filter_by(_locked=False).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def by_name(cls, name):
        """Return the box object whose name is "name" """
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def by_category(cls, _cat_id):
        """Return the box object whose category is "_cat_id" """
        return dbsession.query(cls).filter_by(category_id=int(_cat_id)).all()

    @classmethod
    def by_garbage(cls, _garbage):
        return dbsession.query(cls).filter_by(garbage=_garbage).first()

    @classmethod
    def by_ip_address(cls, ip_addr):
        """
        Returns a box object based on an ip address, supports both ipv4
        and ipv6
        """
        ip = IpAddress.by_address(ip_addr)

        return ip.box if ip is not None else None

    @classmethod
    def flaglist(self, box_id=None):
        flags = self.by_id(box_id).flags
        flaglist = OrderedDict()
        for flag in flags:
            flaglist[flag.uuid] = flag.name
        return flaglist

    @property
    def corporation(self):
        return Corporation.by_id(self.corporation_id)

    @property
    def game_level(self):
        return GameLevel.by_id(self.game_level_id)

    @property
    def category(self):
        return Category.by_id(self.category_id)

    @property
    def flags(self):
        flags = []
        for flag in self._flags:
            if not flag.locked:
                flags.append(flag)
        return flags

    @flags.setter
    def flags(self, flags):
        self._flags = flags

    @property
    def flags_all(self):
        return self._flags

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not 3 <= len(str(value)) <= 32:
            raise ValidationError("Name must be 3 - 32 characters")
        self._name = str(value)

    @property
    def order(self):
        if not self._order:
            self._order = self.id
        return self._order

    @order.setter
    def order(self, value):
        if not value:
            return
        value = int(value)
        if value == self.order:
            return
        i = 1
        boxes = self.all()
        for box in boxes:
            if i == value:
                i += 1
            if self == box:
                self._order = value
            else:
                box._order = i
                i += 1

    @property
    def operating_system(self):
        return self._operating_system if self._operating_system else "?"

    @operating_system.setter
    def operating_system(self, value):
        self._operating_system = str(value)

    @property
    def description(self):
        if self._description is None:
            self._description = ""
        ls = []
        if 0 < len(self._description):
            text = self._description.replace("\r\n", "\n").strip()
            ls.append("%s" % text)
        else:
            ls.append("No information on file.")
        if self.difficulty != "Unknown":
            ls.append("Reported Difficulty: %s" % self.difficulty)
        if not encode(ls[-1], "utf-8").endswith(b"\n"):
            ls[-1] = ls[-1] + "\n"
        return str("\n\n".join(ls))

    @description.setter
    def description(self, value):
        if value is None:
            return ""
        if 1025 < len(value):
            raise ValidationError("Description cannot be greater than 1024 characters")
        self._description = str(value)

    @property
    def difficulty(self):
        return (
            self._difficulty
            if self._difficulty and len(self._difficulty)
            else "Unknown"
        )

    @difficulty.setter
    def difficulty(self, value):
        if value is None:
            return
        if 17 < len(value):
            raise ValidationError("Difficulty cannot be greater than 16 characters")
        self._difficulty = str(value)

    @property
    def capture_message(self):
        return self._capture_message if self._capture_message else ""

    @capture_message.setter
    def capture_message(self, value):
        self._capture_message = str(value)

    @property
    def value(self):
        if not self._value:
            return 0
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = abs(int(value))
        except ValueError:
            raise ValidationError("Reward value must be an integer")

    def locked_corp(self):
        corp = Corporation.by_id(self.corporation_id)
        if corp and corp.locked:
            return True
        return False

    def locked_level(self):
        level = GameLevel.by_id(self.game_level_id)
        if level and level.locked:
            return True
        return False

    @property
    def locked(self):
        """Determines if an admin has locked an box."""
        if self.locked_corp():
            return True
        if self.locked_level():
            return True
        if self._locked == None:
            return False
        return self._locked

    @locked.setter
    def locked(self, value):
        """Setter method for _lock"""
        if value is None:
            value = False
        elif isinstance(value, int):
            value = value == 1
        elif isinstance(value, str):
            value = value.lower() in ["true", "1"]
        assert isinstance(value, bool)
        self._locked = value

    @property
    def avatar(self):
        if self._avatar is not None:
            return self._avatar
        else:
            avatar = get_new_avatar("box")
            if not avatar.startswith("default_"):
                self._avatar = avatar
                dbsession.add(self)
                dbsession.commit()
            return avatar

    @avatar.setter
    def avatar(self, image_data):
        if self.uuid is None:
            self.uuid = str(uuid4())
        if len(image_data) < (1024 * 1024):
            ext = imghdr.what("", h=image_data)
            if ext in ["png", "jpeg", "gif", "bmp"] and not is_xss_image(image_data):
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
                    "Invalid image format, avatar must be: .png .jpeg .gif or .bmp"
                )
        else:
            raise ValidationError("The image is too large")

    @property
    def ipv4s(self):
        """Return a list of all ipv4 addresses"""
        return [ip for ip in self.ip_addresses if ip.version == 4]

    @property
    def ipv6s(self):
        """Return a list of all ipv6 addresses"""
        return [ip for ip in self.ip_addresses if ip.version == 6]

    @property
    def visible_ips(self):
        return [ip for ip in self.ip_addresses if ip.visible is True]

    @property
    def source_code(self):
        return SourceCode.by_box_id(self.id)

    def get_garbage_cfg(self):
        try:
            hex_name = encode(self.name).hex()
        except AttributeError:
            hex_name = encode(self.name, "hex")
        return "[Bot]\nname = %s\ngarbage = %s\n" % (hex_name, self.garbage)

    def is_complete(self, user):
        boxcomplete = True
        for boxflag in self.flags:
            if user.team and boxflag not in user.team.flags:
                boxcomplete = False
                break
        return boxcomplete

    def to_xml(self, parent):
        """Convert object to XML"""
        box_elem = ET.SubElement(parent, "box")
        box_elem.set("gamelevel", "%s" % str(self.game_level.number))
        ET.SubElement(box_elem, "name").text = self.name
        ET.SubElement(box_elem, "operatingsystem").text = self._operating_system
        ET.SubElement(box_elem, "description").text = self._description
        ET.SubElement(box_elem, "capture_message").text = self.capture_message
        ET.SubElement(box_elem, "value").text = str(self.value)
        ET.SubElement(box_elem, "flag_submission_type").text = FlagsSubmissionType(
            self.flag_submission_type
        ).name
        ET.SubElement(box_elem, "difficulty").text = self._difficulty
        ET.SubElement(box_elem, "garbage").text = str(self.garbage)
        ET.SubElement(box_elem, "locked").text = str(
            False if self._locked is None else self._locked
        )
        if self.category_id:
            ET.SubElement(box_elem, "category").text = Category.by_id(
                self.category_id
            ).category
        flags_elem = ET.SubElement(box_elem, "flags")
        flags_elem.set("count", "%s" % str(len(self.flags)))
        for flag in self.flags_all:
            flag.to_xml(flags_elem)
        hints_elem = ET.SubElement(box_elem, "hints")
        count = 0
        for hint in self.hints:
            if hint.flag_id is None:
                hint.to_xml(hints_elem)
                count += 1
        hints_elem.set("count", "%s" % str(count))
        ips_elem = ET.SubElement(box_elem, "ipaddresses")
        ips_elem.set("count", "%s" % str(len(self.ip_addresses)))
        for ip in self.ip_addresses:
            ip.to_xml(ips_elem)
        avatarfile = os.path.join(options.avatar_dir, self.avatar)
        if self.avatar and os.path.isfile(avatarfile):
            with open(avatarfile, mode="rb") as _avatar:
                data = _avatar.read()
                ET.SubElement(box_elem, "avatar").text = encode(data, "base64")
        else:
            ET.SubElement(box_elem, "avatar").text = "none"

    def to_dict(self):
        """Returns editable data as a dictionary"""
        cat = self.category
        if cat:
            category = cat.uuid
        else:
            category = ""
        return {
            "name": self.name,
            "uuid": self.uuid,
            "corporation": self.corporation.uuid,
            "category": category,
            "operating_system": self.operating_system,
            "description": self._description,
            "capture_message": self.capture_message,
            "difficulty": self.difficulty,
            "game_level": self.game_level.uuid,
            "flag_submission_type": self.flag_submission_type,
            "flaglist": self.flaglist(self.id),
            "value": str(self.value),
            "order": str(self.order),
            "locked": str(self.locked),
        }

    def __repr__(self):
        return "<Box - name: %s>" % (self.name,)

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        """Compare based on the order"""
        this, that = self.order, other.order
        if this > that:
            return 1
        elif this == that:
            return 0
        else:
            return -1

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0
