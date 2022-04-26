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


import re
import hashlib
import json
import xml.etree.cElementTree as ET

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.Relationships import team_to_flag, user_to_flag
from sqlalchemy.types import Unicode, Integer, String
from models import dbsession
from models.Box import Box
from models.Team import Team
from models.FlagAttachment import FlagAttachment  # Fix object mapper
from models.FlagChoice import FlagChoice
from models.Penalty import Penalty
from models.BaseModels import DatabaseObject
from libs.ValidationError import ValidationError
from builtins import str
from tornado.options import options
from dateutil.parser import parse
from past.utils import old_div

### Constants
FLAG_STATIC = u"static"
FLAG_REGEX = u"regex"
FLAG_FILE = u"file"
FLAG_DATETIME = u"datetime"
FLAG_CHOICE = u"choice"
FLAG_TYPES = [FLAG_STATIC, FLAG_REGEX, FLAG_FILE, FLAG_DATETIME, FLAG_CHOICE]


class Flag(DatabaseObject):

    """
    Flags that can be captured by players and what not. This object comes in
    these flavors:
        -static
        -regex
        -datetime
        -file
        -choice

    Depending on the cls._type value. For more information see the wiki.
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    box_id = Column(Integer, ForeignKey("box.id"), nullable=False)
    lock_id = Column(Integer, ForeignKey("flag.id", ondelete="SET NULL"), nullable=True)

    _name = Column(Unicode(64), nullable=True)
    _token = Column(Unicode(256), nullable=False)
    _description = Column(Unicode(1024), nullable=False)
    _capture_message = Column(Unicode(512))
    _case_sensitive = Column(Integer, nullable=True)
    _value = Column(Integer, nullable=False)
    _original_value = Column(Integer, nullable=True)
    _order = Column(Integer, nullable=True, index=True)
    _type = Column(Unicode(16), default=False)

    flag_attachments = relationship(
        "FlagAttachment",
        backref=backref("flag", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    flag_choice = relationship(
        "FlagChoice",
        backref=backref("flag", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    penalties = relationship(
        "Penalty",
        backref=backref("flag", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    hints = relationship(
        "Hint",
        backref=backref("flag", lazy="select"),
        cascade="all,delete,delete-orphan",
    )

    FLAG_TYPES = [FLAG_FILE, FLAG_REGEX, FLAG_STATIC, FLAG_DATETIME, FLAG_CHOICE]

    @classmethod
    def all(cls):
        """ Returns a list of all objects in the database """
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """ Returns a the object with id of _id """
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, name):
        """ Returns a the object with name of _name """
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """ Return and object based on a uuid """
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def by_token(cls, token):
        """ Return and object based on a token """
        return dbsession.query(cls).filter_by(_token=str(token)).first()

    @classmethod
    def by_token_and_box_id(cls, token, box_id):
        """ Return and object based on a token """
        return dbsession.query(cls).filter_by(_token=str(token), box_id=box_id).first()

    @classmethod
    def by_type(cls, _type):
        """ Return and object based on a token """
        return dbsession.query(cls).filter_by(_type=str(_type)).all()

    @classmethod
    def team_captures(cls, _id):
        return dbsession.query(team_to_flag).filter_by(flag_id=_id).all()

    @classmethod
    def user_captures(cls, _id):
        return dbsession.query(user_to_flag).filter_by(flag_id=_id).all()

    @classmethod
    def create_flag(cls, _type, box, name, raw_token, description, value):
        """ Check parameters applicable to all flag types """
        creators = {
            FLAG_STATIC: cls._create_flag_static,
            FLAG_REGEX: cls._create_flag_regex,
            FLAG_FILE: cls._create_flag_file,
            FLAG_DATETIME: cls._create_flag_datetime,
            FLAG_CHOICE: cls._create_flag_choice,
        }
        # TODO Don't understand why this is here - name is not unique value
        # and you could simply name questions per box, like "Question 1" - ElJefe 6/1/2018
        # if cls.by_name(name) is not None:
        # raise ValidationError('Flag name already exists in database')
        assert box is not None and isinstance(box, Box)
        new_flag = creators[_type](box, name, raw_token, description, value)
        new_flag._type = _type
        return new_flag

    @classmethod
    def _create_flag_file(cls, box, name, raw_token, description, value):
        """ Check flag file specific parameters """
        token = cls.digest(raw_token)
        return cls(
            box_id=box.id, name=name, token=token, description=description, value=value
        )

    @classmethod
    def _create_flag_regex(cls, box, name, raw_token, description, value):
        """ Check flag regex specific parameters """
        try:
            re.compile(raw_token)
        except:
            raise ValidationError("Flag token is not a valid regex")
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def _create_flag_static(cls, box, name, raw_token, description, value):
        """ Check flag static specific parameters """
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def _create_flag_datetime(cls, box, name, raw_token, description, value):
        """ Check flag datetime specific parameters """
        try:
            parse(raw_token)
        except:
            raise ValidationError("Flag token is not a valid datetime")
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def _create_flag_choice(cls, box, name, raw_token, description, value):
        """ Check flag choice specific parameters """
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def digest(self, data):
        """ Token is SHA1 of data """
        return hashlib.sha1(data).hexdigest()

    def dynamic_value(self, team=None):
        if options.dynamic_flag_value is False:
            return self.value
        elif len(self.team_captures(self.id)) == 0:
            return self.value
        elif team and self in team.flags:
            depreciation = float(old_div(options.flag_value_decrease, 100.0))
            deduction = self.value * depreciation
            if options.dynamic_flag_type == "decay_all":
                reduction = (len(self.team_captures(self.id)) - 1) * deduction
                return max(options.flag_value_minimum, int(self.value - reduction))
            else:
                for index, item in enumerate(self.team_captures(self.id)):
                    if team == Team.by_id(item[0]):
                        reduction = index * deduction
                        return max(
                            options.flag_value_minimum, int(self.value - reduction)
                        )
        else:
            depreciation = float(old_div(options.flag_value_decrease, 100.0))
            deduction = self.value * depreciation
            reduction = len(self.team_captures(self.id)) * deduction
            return max(options.flag_value_minimum, int(self.value - reduction))

    @property
    def game_level(self):
        return self.box.game_level

    @property
    def name(self):
        if self._name and len(self._name) > 0:
            return self._name
        else:
            return "Question %d" % self.order

    @name.setter
    def name(self, value):
        if not len(value) <= 64:
            raise ValidationError(
                "Flag name must be less than 64 characters: %s" % value
            )
        self._name = str(value)

    @property
    def order(self):
        if not self._order:
            self._order = self.box.flags.index(self) + 1
        return self._order

    @order.setter
    def order(self, value):
        if value:
            self._order = int(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = str(value)[:1024]

    @property
    def capture_message(self):
        return self._capture_message if self._capture_message else ""

    @capture_message.setter
    def capture_message(self, value):
        self._capture_message = str(value)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in self.FLAG_TYPES:
            raise ValueError("Invalid flag type")
        self._type = str(value)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = str(value)

    @property
    def case_sensitive(self):
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value):
        if value is None:
            self._case_sensitive = 0
        else:
            self._case_sensitive = value

    @property
    def value(self):
        if self._original_value and self._original_value > self._value:
            """Since value itself is no longer decreased in dynamic scoring
            there is no need for original_value, but for backward compatibility
            if _original_value is GT the value, update the value.
            At some point, we can remove original_value column."""
            self.value = self._original_value
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = abs(int(value))
        except ValueError:
            raise ValidationError("Reward value must be an integer")

    @property
    def get_lock_id(self):
        return self.lock_id

    @get_lock_id.setter
    def set_lock_id(self, value):
        try:
            if value is None:
                self.lock_id = value
            else:
                self.lock_id = abs(int(value))
        except ValueError:
            self.lock_id = None

    @property
    def is_text(self):
        return self._type == FLAG_REGEX or self._type == FLAG_STATIC

    @property
    def is_static(self):
        return self._type == FLAG_STATIC

    @property
    def is_file(self):
        return self._type == FLAG_FILE

    @property
    def box(self):
        return Box.by_id(self.box_id)

    def choices(self):
        # inlucdes the choice uuid - needed for editing choice
        choices = []
        if self._type == FLAG_CHOICE:
            choicelist = FlagChoice.by_flag_id(self.id)
            if choicelist is not None and len(choicelist) > 0:
                for flagchoice in choicelist:
                    choices.append(flagchoice.to_dict())
        return json.dumps(choices)

    def choicelist(self):
        # excludes the choice uuid
        choices = []
        if self._type == FLAG_CHOICE:
            choicelist = FlagChoice.by_flag_id(self.id)
            if choicelist is not None and len(choicelist) > 0:
                for flagchoice in choicelist:
                    choices.append(flagchoice.choice)
        return json.dumps(choices)

    def capture(self, submission):
        if self._type == FLAG_STATIC:
            if self._case_sensitive == 0:
                return (
                    str(self.token).lower().strip() == str(submission).lower().strip()
                )
            else:
                return str(self.token).strip() == str(submission).strip()
        elif self._type == FLAG_REGEX:
            if not self.token.startswith("^(") and not self.token.endswith(")$"):
                self.token = "^(" + self.token + ")$"
            if self._case_sensitive == 0:
                pattern = re.compile(self.token, re.IGNORECASE)
            else:
                pattern = re.compile(self.token)
            return pattern.match(submission) is not None
        elif self._type == FLAG_FILE:
            return self.token == self.digest(submission)
        elif self._type == FLAG_CHOICE:
            return self.token == submission
        elif self._type == FLAG_DATETIME:
            try:
                return parse(self.token) == parse(submission)
            except:
                return False
        else:
            raise ValueError("Invalid flag type, cannot capture")

    def to_xml(self, parent):
        """ Write attributes to XML doc """
        flag_elem = ET.SubElement(parent, "flag")
        flag_elem.set("type", self._type)
        ET.SubElement(flag_elem, "name").text = self._name
        ET.SubElement(flag_elem, "token").text = self.token
        ET.SubElement(flag_elem, "description").text = self.description
        ET.SubElement(flag_elem, "capture_message").text = self.capture_message
        ET.SubElement(flag_elem, "value").text = str(self.value)
        if self.lock_id:
            ET.SubElement(flag_elem, "depends_on").text = Flag.by_id(self.lock_id).name
        ET.SubElement(flag_elem, "case_sensitive").text = str(self.case_sensitive)
        attachments_elem = ET.SubElement(flag_elem, "flag_attachments")
        attachments_elem.set("count", "%s" % str(len(self.flag_attachments)))
        for attachment in self.flag_attachments:
            attachment.to_xml(attachments_elem)
        choice_elem = ET.SubElement(flag_elem, "flag_choices")
        choice_elem.set("count", "%s" % str(len(self.flag_choice)))
        for choice in self.flag_choice:
            ET.SubElement(choice_elem, "choice").text = choice.choice
        from models.Hint import Hint

        xml_hints = Hint.by_flag_id(self.id)
        hints_elem = ET.SubElement(flag_elem, "hints")
        hints_elem.set("count", "%s" % str(len(xml_hints)))
        for hint in xml_hints:
            if hint.flag_id is not None:
                hint.to_xml(hints_elem)

    def to_dict(self):
        """ Returns public data as a dict """
        box = Box.by_id(self.box_id)
        if self.lock_id:
            lock_uuid = Flag.by_id(self.lock_id).uuid
        else:
            lock_uuid = ""
        case_sensitive = self.case_sensitive
        if case_sensitive != 0:
            case_sensitive = 1
        return {
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description,
            "capture_message": self.capture_message,
            "value": self.value,
            "box": box.uuid,
            "token": self.token,
            "lock_uuid": lock_uuid,
            "case-sensitive": case_sensitive,
            "flagtype": self.type,
            "choices": self.choices(),
            "order": self.order,
        }

    def __repr__(self):
        return "<Flag - name:%s, type:%s >" % (self.name, str(self._type))
