# -*- coding: utf-8 -*-
"""
Unit tests for everything in handlers/
"""

from models import dbsession
from models.User import User
from models.Team import Team
from tests.HTTPClient import ApplicationTest
from tests.Helpers import *
from tornado.options import options


class TestPublicHandlers(ApplicationTest):
    """ Test functionality in handlers/PublicHandlers.py """

    def test_home_page_get(self):
        self.get("/")(self.stop)
        rsp, body = self.wait()
        assert "<h2>A Game of Hackers</h2>" in body

    def test_login_get(self):
        self.get("/login")(self.stop)
        rsp, body = self.wait()
        assert '<form class="form-signin" action="/login"' in body

    def test_login_post(self):
        user = create_user()
        self._login_failure()
        self._login_success()
        dbsession.delete(user)
        dbsession.commit()

    def _login_success(self):
        form = {"account": "HacKer", "password": "TestPassword"}
        self.post("/login", data=form)(self.stop)
        rsp, body = self.wait()
        # Sould redirect to firstlogin
        print(rsp, body)
        assert "Incoming Transmission" in body

    def _login_failure(self):
        form = {"account": "HacKer", "password": "A" * 16}
        self.post("/login", data=form)(self.stop)
        rsp, body = self.wait()
        assert "Bad username and/or password, try again" in body

    def test_registration_get(self):
        self.get("/registration")(self.stop)
        rsp, body = self.wait()
        assert '<form class="form-horizontal" action="/registration"' in body

    def test_registration_post(self):
        form = {
            "handle": "foobar",
            "team_name": "TestTeam",
            "motto": "Unit Tests are Cool",
            "pass1": "12345678901234567890",
            "pass2": "12345678901234567890",
            "bpass": "123456",
        }
        self._registration_post_token(form)
        self._registration_post_team_name(form)

    def _registration_post_token(self, form):
        options.restrict_registration = True
        form["token"] = "NotARealRegToken"
        self.post("/registration", data=form)(self.stop)
        rsp, body = self.wait()
        assert "Invalid registration token" in body
        options.restrict_registration = False

    def _registration_post_team_name(self, form):
        form["team_name"] = ""
        self.post("/registration", data=form)(self.stop)
        rsp, body = self.wait()
        assert "Team name must be 3 - 16 characters" in body
        form["team_name"] = "A" * 17
        self.post("/registration", data=form)(self.stop)
        rsp, body = self.wait()
        assert "Team name must be 3 - 16 characters" in body

    def test_fake_robots_get(self):
        self.get("/robots")(self.stop)
        rsp, body = self.wait()
        assert "User-agent: *" in body
        self.get("/robots.txt")(self.stop)
        rsp, body = self.wait()
        assert "User-agent: *" in body

    def test_about_get(self):
        self.get("/about")(self.stop)
        rsp, body = self.wait()
        assert "<h1>About" in body


# class TestMissionHandlers(ApplicationTest):
#
#    def setUp(self):
#        self.username = 'foobar'
#        self.password = 'testpassword123456'
