
import unittest

from models import dbsession
from models.Team import Team
from models.User import User


class TestTeam(unittest.TestCase):

    def setUp(self):
        self.team = Team()
        self.team.name = "TestTeam"
        self.team.motto = "TestMotto"
        dbsession.add(self.team)
        dbsession.commit()

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
        self.user = User()
        self.user.handle = "HacKer"
        self.user.password = "TestPassword"
        self.user.bank_password = "Test123"
        dbsession.add(self.user)
        dbsession.commit()

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