# -*- coding: utf-8 -*-
"""
Unit tests for everything in models/
"""


import unittest

from models import dbsession
from models.Team import Team
from models.User import User
from models.Corporation import Corporation
from models.Box import Box
from models.GameLevel import GameLevel
from models.Flag import (
    Flag,
    FLAG_STATIC,
    FLAG_REGEX,
    FLAG_FILE,
    FLAG_DATETIME,
    FLAG_CHOICE,
)
from libs.ValidationError import ValidationError
from libs.StringCoding import encode
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

        dbsession.add(self.static_flag)
        dbsession.add(self.regex_flag)
        dbsession.add(self.file_flag)
        dbsession.add(self.choice_flag)
        dbsession.add(self.datetime_flag)
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
