# -*- coding: utf-8 -*-
"""
Unit tests for everything in models/
"""


import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tornado.ioloop import IOLoop

from libs.StringCoding import encode
from libs.ValidationError import ValidationError
from models import dbsession
from models.Box import Box
from models.Corporation import Corporation
from models.Flag import (
    FLAG_CHOICE,
    FLAG_DATETIME,
    FLAG_FILE,
    FLAG_REGEX,
    FLAG_REMOTE,
    FLAG_REMOTESTRING,
    FLAG_STATIC,
    Flag,
)
from models.GameLevel import GameLevel
from models.Team import Team
from models.User import User
from tests.Helpers import *


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = create_team()

    def tearDown(self):
        dbsession.delete(self.team)
        dbsession.commit()

    def test_name(self):
        assert self.team.name == "TestTeam"
        with self.assertRaises(ValidationError):
            self.team.name = ""
        with self.assertRaises(ValidationError):
            self.team.name = "A" * 25

    def test_motto(self):
        assert self.team.motto == "TestMotto"
        with self.assertRaises(ValidationError):
            self.team.motto = "A" * 35


class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = create_user()

    def tearDown(self):
        dbsession.delete(self.user)
        dbsession.commit()

    def test_handle(self):
        assert self.user.handle == "HacKer"
        with self.assertRaises(ValidationError):
            self.user.handle = ""
        with self.assertRaises(ValidationError):
            self.user.handle = "A" * 20

    def test_password(self):
        assert not self.user.validate_password("")
        assert self.user.validate_password("TestPassword")
        assert not self.user.validate_password("WrongPwd")

    def test_bank_password(self):
        assert self.user.validate_bank_password("Test123")
        assert not self.user.validate_password("Wrong")
        with self.assertRaises(ValidationError):
            self.user.bank_password = "A" * 100


class TestGameLevel(unittest.TestCase):
    def setUp(self):
        self.game_level = GameLevel()
        self.game_level.number = 1
        self.game_level.buyout = 1000
        dbsession.add(self.game_level)
        dbsession.commit()

    def tearDown(self):
        dbsession.delete(self.game_level)
        dbsession.commit()

    def test_number(self):

        assert 0 <= self.game_level.number
        self.game_level.number = "1"
        assert self.game_level.number == 1
        self.game_level.number = " 1 "
        assert self.game_level.number == 1
        with self.assertRaises(ValidationError):
            self.game_level.number = "A"

    def test_buyout(self):
        assert 0 <= self.game_level.buyout
        self.game_level.buyout = -1000
        assert 0 <= self.game_level.buyout
        self.game_level.buyout = "1000"
        assert self.game_level.buyout == 1000
        with self.assertRaises(ValidationError):
            self.game_level.buyout = "A"


class TestCorporation(unittest.TestCase):
    def setUp(self):
        self.corp = create_corp()

    def tearDown(self):
        dbsession.delete(self.corp)
        dbsession.commit()

    def test_name(self):
        assert self.corp.name == "TestCorp"
        with self.assertRaises(ValidationError):
            self.corp.name = "A" * 35


class TestBox(unittest.TestCase):
    def setUp(self):
        self.box, self.corp = create_box()

    def tearDown(self):
        dbsession.delete(self.corp)
        dbsession.commit()

    def test_name(self):
        assert self.box.name == "TestBox"
        with self.assertRaises(ValidationError):
            self.box.name = ""
        with self.assertRaises(ValidationError):
            self.box.name = "A" * 35

    def test_description(self):
        with self.assertRaises(ValidationError):
            self.box.description = "A" * 1030


class TestFlag(unittest.TestCase):
    def setUp(self):
        self.box, self.corp = create_box()
        self.static_flag = Flag.create_flag(
            _type=FLAG_STATIC,
            box=self.box,
            name="Static Flag",
            raw_token="statictoken",
            description="A static test token",
            value=100,
        )
        self.regex_flag = Flag.create_flag(
            _type=FLAG_REGEX,
            box=self.box,
            name="Regex Flag",
            raw_token="(f|F)oobar",
            description="A regex test token",
            value=200,
        )
        self.file_flag = Flag.create_flag(
            _type=FLAG_FILE,
            box=self.box,
            name="File Flag",
            raw_token=encode("fdata"),
            description="A file test token",
            value=300,
        )
        self.choice_flag = Flag.create_flag(
            _type=FLAG_CHOICE,
            box=self.box,
            name="Choice Flag",
            raw_token=encode("fdata"),
            description="A choice test token",
            value=400,
        )
        self.datetime_flag = Flag.create_flag(
            _type=FLAG_DATETIME,
            box=self.box,
            name="Datetime Flag",
            raw_token="2018-06-22 18:00:00",
            description="A datetime test token",
            value=500,
        )
        self.remote_flag = Flag.create_flag(
            _type=FLAG_REMOTE,
            box=self.box,
            name="Remote Flag",
            raw_token="remote-id",
            description="A remotely checked flag",
            value=600,
        )
        self.remote_string_flag = Flag.create_flag(
            _type=FLAG_REMOTESTRING,
            box=self.box,
            name="Remote String Flag",
            raw_token="remote-string-id",
            description="A remotely checked string flag",
            value=700,
        )

        dbsession.add(self.static_flag)
        dbsession.add(self.regex_flag)
        dbsession.add(self.file_flag)
        dbsession.add(self.choice_flag)
        dbsession.add(self.datetime_flag)
        dbsession.add(self.remote_flag)
        dbsession.add(self.remote_string_flag)
        dbsession.commit()

    def tearDown(self):
        dbsession.delete(self.corp)
        dbsession.commit()

    def test_name(self):
        with self.assertRaises(ValidationError):
            self.static_flag.name = "A" * 65

    def test_static_capture(self):
        assert self.static_flag.capture("statictoken")
        assert not self.static_flag.capture("nottoke")

    def test_regex_capture(self):
        assert self.regex_flag.capture("foobar")
        assert self.regex_flag.capture("Foobar")
        assert not self.regex_flag.capture("asdf")

    def test_file_capture(self):
        assert self.file_flag.capture(encode("fdata"))
        assert not self.file_flag.capture(encode("other"))

    def test_choice_capture(self):
        assert self.file_flag.capture(encode("fdata"))
        assert not self.file_flag.capture(encode("other"))

    def test_datetime_capture(self):
        assert self.datetime_flag.capture("2018-06-22 18:00:00")
        assert not self.datetime_flag.capture("2018-06-21 16:00:00")

    def test_remote_capture_is_async(self):
        response = SimpleNamespace(
            code=200,
            body=b'{"status": "success", "message": "captured"}',
        )
        request_data = {}

        async def send_request(flag, data):
            request_data.update(data)
            return response

        with patch.object(Flag, "_send_remote_flag_request", send_request):
            captured = IOLoop.current().run_sync(
                lambda: self.remote_flag.capture_async(
                    "ignored", player_ip="192.0.2.1"
                )
            )

        assert captured
        assert self.remote_flag.status == "success"
        assert self.remote_flag.message == "captured"
        assert request_data == {
            "flag_token": "remote-id",
            "player_ip": "192.0.2.1",
        }

    def test_remote_string_capture_sends_submission(self):
        response = SimpleNamespace(
            code=200,
            body=b'{"status": "fail", "message": "try again"}',
        )
        request_data = {}

        async def send_request(flag, data):
            request_data.update(data)
            return response

        with patch.object(Flag, "_send_remote_flag_request", send_request):
            captured = IOLoop.current().run_sync(
                lambda: self.remote_string_flag.capture_async("player answer")
            )

        assert not captured
        assert self.remote_string_flag.status == "fail"
        assert self.remote_string_flag.message == "try again"
        assert request_data == {
            "flag_token": "remote-string-id",
            "submission": "player answer",
        }

    def test_remote_response_rejects_invalid_payloads(self):
        invalid_responses = (
            SimpleNamespace(code=200, body=b"not-json"),
            SimpleNamespace(code=200, body=b"null"),
            SimpleNamespace(code=200, body=b'{"status": "unknown"}'),
            SimpleNamespace(code=200, body=b'{"status": []}'),
            SimpleNamespace(
                code=200,
                body=b'{"status": "success", "message": {}}',
            ),
            SimpleNamespace(code=503, body=b""),
        )

        for response in invalid_responses:
            with self.subTest(response=response):
                assert not self.remote_flag._process_remote_flag_response(response)
                assert self.remote_flag.status == "error"

    def test_remote_response_preserves_server_error(self):
        response = SimpleNamespace(
            code=200,
            body=b'{"status": "error", "message": "maintenance"}',
        )

        assert not self.remote_flag._process_remote_flag_response(response)
        assert self.remote_flag.status == "error"
        assert self.remote_flag.message == "maintenance"

    def test_remote_capture_requires_async_api(self):
        with self.assertRaises(ValueError):
            self.remote_flag.capture("ignored")
