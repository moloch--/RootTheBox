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


import hashlib
import json
import re
import xml.etree.ElementTree as ET
from builtins import str
from urllib.parse import urlencode
from uuid import uuid4

from dateutil.parser import parse
from past.utils import old_div
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.types import Boolean, Integer, String, Unicode
from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest
from tornado.options import options

from libs.ValidationError import ValidationError
from models import dbsession
from models.BaseModels import DatabaseObject
from models.Box import Box
from models.FlagAttachment import FlagAttachment  # Fix object mapper
from models.FlagChoice import FlagChoice
from models.Penalty import Penalty
from models.Relationships import team_to_flag, user_to_flag
from models.Team import Team

### Constants
FLAG_STATIC = "static"
FLAG_REGEX = "regex"
FLAG_FILE = "file"
FLAG_DATETIME = "datetime"
FLAG_CHOICE = "choice"
FLAG_REMOTE = "remote"
FLAG_REMOTESTRING = "remotestring"
FLAG_TYPES = [
    FLAG_STATIC,
    FLAG_REGEX,
    FLAG_FILE,
    FLAG_DATETIME,
    FLAG_CHOICE,
    FLAG_REMOTE,
    FLAG_REMOTESTRING,
]
REMOTE_FLAG_STATUSES = frozenset(("success", "fail", "error"))


class Flag(DatabaseObject):

    """
    Flags that can be captured by players and what not. This object comes in
    these flavors:
        -static
        -regex
        -datetime
        -file
        -choice
        -remote
        -remotestring

    Depending on the cls._type value. For more information see the wiki.
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    box_id = Column(Integer, ForeignKey("box.id"), nullable=False)
    lock_id = Column(Integer, ForeignKey("flag.id", ondelete="SET NULL"), nullable=True)

    _name = Column(Unicode(64), nullable=True)
    _token = Column(Unicode(256), nullable=False)
    _plain_answer = Column(Unicode(256)) # https://github.com/moloch--/RootTheBox/issues/601
    _description = Column(Unicode(4096), nullable=False)
    _capture_message = Column(Unicode(4096))
    _case_sensitive = Column(Integer, nullable=True)
    _value = Column(Integer, nullable=False)
    _original_value = Column(Integer, nullable=True)
    _order = Column(Integer, nullable=True, index=True)
    _type = Column(Unicode(16), default=False)
    _locked = Column(Boolean, default=False, nullable=False)

    status = ""
    message = "Default Message"

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

    FLAG_TYPES = [
        FLAG_FILE,
        FLAG_REGEX,
        FLAG_STATIC,
        FLAG_DATETIME,
        FLAG_CHOICE,
        FLAG_REMOTE,
        FLAG_REMOTESTRING,
    ]

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, name):
        """Returns a the object with name of _name"""
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def by_token(cls, token):
        """Return and object based on a token"""
        return dbsession.query(cls).filter_by(_token=str(token)).first()

    @classmethod
    def by_token_and_box_id(cls, token, box_id):
        """Return and object based on a token"""
        return dbsession.query(cls).filter_by(_token=str(token), box_id=box_id).first()

    @classmethod
    def by_type(cls, _type):
        """Return and object based on a token"""
        return dbsession.query(cls).filter_by(_type=str(_type)).all()

    @classmethod
    def get_children(cls, _id):
        return dbsession.query(cls).filter_by(lock_id=_id).all()

    @classmethod
    def team_captures(cls, _id):
        return dbsession.query(team_to_flag).filter_by(flag_id=_id).all()

    @classmethod
    def user_captures(cls, _id):
        return dbsession.query(user_to_flag).filter_by(flag_id=_id).all()

    @classmethod
    def create_flag(cls, _type, box, name, raw_token, description, value):
        """Check parameters applicable to all flag types"""
        creators = {
            FLAG_STATIC: cls._create_flag_static,
            FLAG_REGEX: cls._create_flag_regex,
            FLAG_FILE: cls._create_flag_file,
            FLAG_DATETIME: cls._create_flag_datetime,
            FLAG_CHOICE: cls._create_flag_choice,
            FLAG_REMOTE: cls._create_flag_remote,
            FLAG_REMOTESTRING: cls._create_flag_remotestring,
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
        """Check flag file specific parameters"""
        token = cls.digest(raw_token)
        return cls(
            box_id=box.id, name=name, token=token, description=description, value=value
        )

    @classmethod
    def _create_flag_regex(cls, box, name, raw_token, description, value):
        """Check flag regex specific parameters"""
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
        """Check flag static specific parameters"""
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def _create_flag_datetime(cls, box, name, raw_token, description, value):
        """Check flag datetime specific parameters"""
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
        """Check flag choice specific parameters"""
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def _create_flag_remote(cls, box, name, raw_token, description, value):
        """Check flag remote specific parameters"""
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )

    @classmethod
    def _create_flag_remotestring(cls, box, name, raw_token, description, value):
        """Check flag remotestring specific parameters"""
        return cls(
            box_id=box.id,
            name=name,
            token=raw_token,
            description=description,
            value=value,
        )


    @classmethod
    def digest(self, data):
        """Token is SHA1 of data"""
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
        self._description = str(value)[:4096]

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
    def is_remote(self):
        return self._type == FLAG_REMOTE

    @property
    def is_remotestring(self):
        return self._type == FLAG_REMOTESTRING

    @property
    def box(self):
        return Box.by_id(self.box_id)

    @property
    def locked(self):
        """Determines if an admin has locked an flag."""
        if self._locked is None:
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

    def capture(self, submission, **kwargs):
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
        elif self._type in (FLAG_REMOTE, FLAG_REMOTESTRING):
            raise ValueError("Remote flags must be captured asynchronously")
        else:
            raise ValueError("Invalid flag type, cannot capture")

    async def capture_async(self, submission, **kwargs):
        """Capture a flag without blocking the Tornado event loop."""
        if self._type in (FLAG_REMOTE, FLAG_REMOTESTRING):
            return await self.capture_remote_flag(submission, **kwargs)
        return self.capture(submission, **kwargs)

    async def capture_remote_flag(self, submission, **kwargs):
        """Submit this flag to the configured remote flag server.

        Validates the flag type, sends the request to the remote server, and
        updates ``self.status`` and ``self.message`` with the result.

        Possible values for self.status:
        success, fail, error

        Args:
            submission: The submitted flag value. It is sent only for
                ``FLAG_REMOTESTRING`` flags.
            **kwargs: Optional request metadata. If ``player_ip`` is provided,
                it is included in the request payload.

        Returns:
            bool: ``True`` if the remote server returns a ``"success"`` status;
            otherwise ``False``.
        """

        if not self._validate_remote_flag_request():
            return False

        data = self._build_remote_flag_data(submission, **kwargs)
        reply = await self._send_remote_flag_request(data)

        if reply is None:
            return False

        return self._process_remote_flag_response(reply)

    def _validate_remote_flag_request(self):
        if self._type not in (FLAG_REMOTE, FLAG_REMOTESTRING):
            return self._set_remote_error("Wrong flagtype for remoteflag")

        return True

    def _set_remote_error(self, message):
        self.status = "error"
        self.message = message
        return False

    def _build_remote_flag_data(self, submission, **kwargs):
        data = {
            "flag_token": self.token,
        }

        if "player_ip" in kwargs:
            data["player_ip"] = kwargs["player_ip"]

        if self._type == FLAG_REMOTESTRING:
            data["submission"] = submission

        return data

    def _get_remote_flag_url(self):
        return (
            f"{options.remote_protocol}://"
            f"{options.remote_domain}:"
            f"{options.remote_port}"
            f"{options.remote_path}"
        )

    async def _send_remote_flag_request(self, data):
        try:
            request = HTTPRequest(
                url=self._get_remote_flag_url(),
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=urlencode(data).encode("utf-8"),
                request_timeout=options.remote_timeout,
            )
            return await AsyncHTTPClient().fetch(request, raise_error=False)
        except (HTTPClientError, ValueError) as error:
            self._set_remote_error(f"Request to Flagserver failed: {error}")

        return None

    def _process_remote_flag_response(self, reply):
        if reply.code != 200:
            return self._set_remote_error(
                f"Request to Flagserver returned status {reply.code}"
            )

        try:
            response_data = json.loads(reply.body.decode("utf-8"))
        except (AttributeError, UnicodeDecodeError, json.JSONDecodeError):
            return self._set_remote_error(
                "Reply from FlagCheckServer is not valid JSON"
            )

        if not isinstance(response_data, dict):
            return self._set_remote_error(
                "Reply from FlagCheckServer is not a JSON object"
            )

        status = response_data.get("status")
        if not isinstance(status, str) or status not in REMOTE_FLAG_STATUSES:
            return self._set_remote_error(
                "Reply from FlagCheckServer contains an invalid status"
            )

        message = response_data.get("message", "No message from FlagServer")
        if not isinstance(message, str):
            return self._set_remote_error(
                "Reply from FlagCheckServer contains an invalid message"
            )

        self.status = status
        self.message = message

        return self.status == "success"

    def to_xml(self, parent):
        """Write attributes to XML doc"""
        flag_elem = ET.SubElement(parent, "flag")
        flag_elem.set("type", self._type)
        ET.SubElement(flag_elem, "name").text = self._name
        ET.SubElement(flag_elem, "token").text = self.token
        ET.SubElement(flag_elem, "description").text = self.description
        ET.SubElement(flag_elem, "capture_message").text = self.capture_message
        ET.SubElement(flag_elem, "value").text = str(self.value)
        ET.SubElement(flag_elem, "plain_answer").text = str(self._plain_answer)
        ET.SubElement(flag_elem, "locked").text = str(self.locked)
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
        """Returns public data as a dict"""
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
            "locked": self.locked,
        }

    def __repr__(self):
        return "<Flag - name:%s, type:%s >" % (self.name, str(self._type))

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
