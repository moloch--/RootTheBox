
import unittest

from models import dbsession
from models.Team import Team
from models.User import User
from models.Corporation import Corporation
from models.Box import Box
from models.GameLevel import GameLevel
from models.Flag import Flag, FLAG_STATIC, FLAG_REGEX, FLAG_FILE


def create_team():
    team = Team()
    team.name = "TestTeam"
    team.motto = "TestMotto"
    dbsession.add(team)
    dbsession.commit()
    return team

def create_user():
    user = User()
    user.handle = "HacKer"
    user.password = "TestPassword"
    user.bank_password = "Test123"
    dbsession.add(user)
    dbsession.commit()
    return user

def create_corp():
    corp = Corporation()
    corp.name = "TestCorp"
    dbsession.add(corp)
    dbsession.commit()
    return corp

def create_box(corp=None):
    if corp is None:
        corp = create_corp()
    game_level = GameLevel.all()[0]
    box = Box(corporation_id=corp.id, game_level_id=game_level.id)
    box.name = "TestBox"
    box.description = "Some description"
    box.difficuly = "Easy"
    corp.boxes.append(box)
    dbsession.add(box)
    dbsession.commit()
    return box, corp


class TestTeam(unittest.TestCase):

    def setUp(self):
        self.team = create_team()

    def tearDown(self):
        dbsession.delete(self.team)
        dbsession.commit()

    def test_name(self):
        assert self.team.name == "TestTeam"
        with self.assertRaises(ValueError):
            self.team.name = ""
        with self.assertRaises(ValueError):
            self.team.name = "A" * 20

    def test_motto(self):
        assert self.team.motto == "TestMotto"
        with self.assertRaises(ValueError):
            self.team.motto = "A" * 35


class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = create_user()

    def tearDown(self):
        dbsession.delete(self.user)
        dbsession.commit()

    def test_handle(self):
        assert self.user.handle == "HacKer"
        with self.assertRaises(ValueError):
            self.user.handle = ""
        with self.assertRaises(ValueError):
            self.user.handle = "A" * 20

    def test_password(self):
        assert not self.user.validate_password("")
        assert self.user.validate_password("TestPassword")
        assert not self.user.validate_password("WrongPwd")

    def test_bank_password(self):
        assert self.user.validate_bank_password("Test123")
        assert not self.user.validate_password("Wrong")
        with self.assertRaises(ValueError):
            self.user.bank_password = "A" * 100


class TestCorporation(unittest.TestCase):

    def setUp(self):
        self.corp = create_corp()

    def tearDown(self):
        dbsession.delete(self.corp)
        dbsession.commit()

    def test_name(self):
        assert self.corp.name == "TestCorp"
        with self.assertRaises(ValueError):
            self.corp.name = ""
        with self.assertRaises(ValueError):
            self.corp.name = "A" * 35


class TestBox(unittest.TestCase):

    def setUp(self):
        self.box, self.corp = create_box()

    def tearDown(self):
        dbsession.delete(self.corp)
        dbsession.commit()

    def test_name(self):
        assert self.box.name == "TestBox"
        with self.assertRaises(ValueError):
            self.box.name = ""
        with self.assertRaises(ValueError):
            self.box.name = "A" * 20

    def test_description(self):
        with self.assertRaises(ValueError):
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
            raw_token="fdata",
            description="A file test token",
            value=300,
        )
        dbsession.add(self.static_flag)
        dbsession.add(self.regex_flag)
        dbsession.add(self.file_flag)
        dbsession.commit()

    def tearDown(self):
        dbsession.delete(self.corp)
        dbsession.commit()

    def test_name(self):
        with self.assertRaises(ValueError):
            self.static_flag.name = ""
        with self.assertRaises(ValueError):
            self.static_flag.name = "A" * 20

    def test_static_capture(self):
        assert self.static_flag.capture("statictoken")
        assert not self.static_flag.capture("nottoke")

    def test_regex_capture(self):
        assert self.regex_flag.capture("foobar")
        assert self.regex_flag.capture("Foobar")
        assert not self.regex_flag.capture("asdf")

    def test_file_capture(self):
        assert self.file_flag.capture("fdata")
        assert not self.file_flag.capture("other")