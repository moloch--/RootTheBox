# -*- coding: utf-8 -*-
"""
Created on Mar 13, 2012

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
----------------------------------------------------------------------------

This file contains code for managing user accounts

"""
# pylint: disable=no-member


try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    import urllib.request as urlrequest
except ImportError:
    import urllib2 as urlrequest
import logging
import tornado
import json

from models.Theme import Theme
from models.User import User
from models.Box import Box
from libs.EventManager import EventManager
from libs.ValidationError import ValidationError
from libs.SecurityDecorators import authenticated
from libs.XSSImageCheck import IMG_FORMATS
from builtins import str
from .BaseHandlers import BaseHandler
from tornado.options import options


class HomeHandler(BaseHandler):
    """Allow for public view of user page if scoreboard set to public"""

    def get(self, *args, **kwargs):
        """Display the default user page"""
        user = self.get_current_user()
        if user:
            admin = user.is_admin()
        else:
            admin = False
        uuid = self.get_argument("id", None)
        display_user = User.by_uuid(uuid)
        visitor = False
        if not user and (options.scoreboard_visibility != "public" or not display_user):
            self.redirect("/login")
            return
        elif display_user and (not user or display_user != user):
            user = display_user
            visitor = True
        if not user:
            self.redirect("/login")
            return
        gamestate = self.application.settings["scoreboard_state"].get("teams")
        try:
            stats = self.memcached.stats().get("127.0.0.1")
            activeconnections = int(stats.get("curr_connections"))
        except:
            activeconnections = None
        if uuid is None and user.is_admin():
            self.timer()
            self.render(
                "admin/home.html",
                user=user,
                boxcount=len(Box.all()),
                teamcount=len(gamestate),
                usercount=len(User.all_users()),
                activeconnections=activeconnections,
            )
        else:
            game_started = self.application.settings["game_started"] or user.is_admin()
            rank = len(gamestate) + 1
            for i, team in enumerate(gamestate):
                if team == user.team.name:
                    rank = i + 1
                    break
            self.render(
                "user/home.html",
                user=user,
                game_started=game_started,
                visitor=visitor,
                rank=rank,
                scoreboard_visible=options.scoreboard_visibility != "admins",
            )


class SettingsHandler(BaseHandler):
    """Modify user controlled attributes"""

    @authenticated
    def get(self, *args, **kwargs):
        """Display the user settings"""
        self.render_page()

    @authenticated
    def post(self, *args, **kwargs):
        """Calls function based on parameter"""
        post_functions = {
            "user_avatar": self.post_avatar,
            "team_avatar": self.post_team_avatar,
            "password": self.post_password,
            "bank_password": self.post_bankpassword,
            "theme": self.post_theme,
            "motto": self.post_motto,
            "email": self.post_email,
        }
        if len(args) == 1 and args[0] in post_functions:
            post_functions[args[0]]()
        else:
            self.render_page()

    def render_page(self, errors=[], success=[]):
        """Small wrap for self.render to cut down on lengthy params"""
        user = self.get_current_user()
        self.add_content_policy("script", "'unsafe-eval'")
        current_theme = Theme.by_id(self.session["theme_id"])
        self.add_content_policy("script", "www.google.com")
        self.add_content_policy("img", "www.google.com")
        self.render(
            "user/settings.html",
            errors=errors,
            success=success,
            current_theme=current_theme,
            user=user,
        )

    def post_avatar(self, *args, **kwargs):
        """
        Saves avatar - Reads file header an only allows approved formats
        """
        user = self.get_current_user()
        if self.get_argument("user_avatar_select", None):
            avatar = self.get_argument("user_avatar_select", "")
            if avatar.lower().endswith(tuple(IMG_FORMATS)):
                user._avatar = avatar
                self.dbsession.add(user)
                self.dbsession.commit()
                self.render_page(success=["Updated avatar"])
        elif hasattr(self.request, "files") and "user_avatar" in self.request.files:
            try:
                user.avatar = self.request.files["user_avatar"][0]["body"]
                self.dbsession.add(user)
                self.dbsession.commit()
                self.render_page(success=["Updated avatar"])
            except ValidationError as error:
                self.render_page(errors=[str(error)])
        else:
            self.render_page(errors=["Please provide an image"])

    def post_team_avatar(self, *args, **kwargs):
        """
        Saves team avatar - Reads file header an only allows approved formats
        """
        user = self.get_current_user()
        if not user.team:
            self.render_page(errors=["Not assigned to a team"])
        elif self.get_argument("team_avatar_select", None):
            avatar = self.get_argument("team_avatar_select", "")
            if avatar.lower().endswith(tuple(IMG_FORMATS)):
                user.team._avatar = avatar
                self.dbsession.add(user)
                self.dbsession.commit()
                if self.config.teams:
                    self.render_page(success=["Updated team avatar"])
                else:
                    self.render_page(success=["Updated avatar"])
        elif hasattr(self.request, "files") and "team_avatar" in self.request.files:
            try:
                if user.team is None:
                    self.render_page(errors=["You do not belong to a team!"])
                else:
                    user.team.avatar = self.request.files["team_avatar"][0]["body"]
                    self.dbsession.add(user)
                    self.dbsession.commit()
                    if self.config.teams:
                        self.render_page(success=["Updated team avatar"])
                    else:
                        self.render_page(success=["Updated avatar"])
            except ValidationError as error:
                self.render_page(errors=[str(error)])
        else:
            self.render_page(errors=["Please provide an image"])

    def post_theme(self, *args, **kwargs):
        """Change per-user theme"""
        if not options.allow_user_to_change_theme:
            self.render_page(errors=["Users are not allowed to change themes"])
            return
        theme = Theme.by_uuid(self.get_argument("theme_uuid", ""))
        if theme is not None:
            self.session["theme_id"] = theme.id
            self.session["theme"] = [str(f) for f in theme.files]
            self.session.save()
            user = self.get_current_user()
            user.theme_id = theme.id
            self.dbsession.add(user)
            self.dbsession.commit()
            self.render_page()
        else:
            self.render_page(errors=["Theme does not exist."])

    def post_motto(self, *args, **kwargs):
        """Change team motto"""
        user = self.get_current_user()
        if not user.team:
            self.render_page(errors=["Not assigned to a team"])
        else:
            user.team.motto = self.get_argument("motto", "")
        self.dbsession.add(user)
        self.dbsession.commit()
        self.render_page(success=["Successfully updated Motto."])

    def post_email(self, *args, **kwargs):
        """Change user email"""
        user = self.get_current_user()
        user.email = self.get_argument("email", "")
        self.dbsession.add(user)
        self.dbsession.commit()
        self.render_page(success=["Successfully updated email address."])

    def post_password(self, *args, **kwargs):
        """Called on POST request for password change"""
        self.set_password(
            self.get_current_user(),
            self.get_argument("old_password", ""),
            self.get_argument("new_password", ""),
            self.get_argument("new_password2", ""),
        )

    def set_password(self, user, old_password, new_password, new_password2):
        """Sets a users password"""
        if user.validate_password(old_password):
            if new_password == new_password2:
                if (
                    len(new_password) >= options.min_user_password_length
                    or self.config.debug
                ):
                    user.password = new_password
                    self.dbsession.add(user)
                    self.dbsession.commit()
                    self.render_page(success=["Successfully updated password"])
                else:
                    self.render_page(
                        errors=[
                            "Password must be at least %d characters "
                            % (options.min_user_password_length,)
                        ]
                    )
            else:
                self.render_page(errors=["New password's didn't match"])
        else:
            self.render_page(errors=["Invalid old password"])

    def post_bankpassword(self):
        """Update user's bank password"""
        old_bankpw = self.get_argument("old_bpassword", "")
        user = self.get_current_user()
        if user.validate_bank_password(old_bankpw):
            if self.config.use_recaptcha:
                self.verify_recaptcha()
            else:
                self.set_bankpassword()
        else:
            self.render_page(errors=["Invalid old password."])

    def set_bankpassword(self):
        user = self.get_current_user()
        new_bankpw = self.get_argument("new_bpassword", "")
        if 0 < len(new_bankpw) <= options.max_password_length:
            user.bank_password = new_bankpw
            self.dbsession.add(user)
            self.dbsession.commit()
            self.render_page(success=["Successfully updated bank password"])
        else:
            self.render_page(
                errors=[
                    "Invalid password - max length %s."
                    % str(options.max_password_length)
                ]
            )

    def verify_recaptcha(self):
        """Checks recaptcha"""
        recaptcha_response = self.get_argument("g-recaptcha-response", None)
        if recaptcha_response:
            recaptcha_req_data = {
                "secret": self.config.recaptcha_secret_key,
                "remoteip": self.request.remote_ip,
                "response": recaptcha_response,
            }
            try:
                recaptcha_req_body = urlencode(recaptcha_req_data).encode("utf-8")
                request = urlrequest.Request(self.RECAPTCHA_URL, recaptcha_req_body)
                response = urlrequest.urlopen(request)
                self.recaptcha_callback(response)
            except tornado.httpclient.HTTPError:
                logging.exception("Recaptcha AsyncHTTP request threw an exception")
                self.recaptcha_callback(None)
                self.render_page(errors=["Error making backend recaptcha request"])
        else:
            self.render_page(errors=["Invalid captcha, try again"])

    def recaptcha_callback(self, response):
        """
        Validates recaptcha response
        Recaptcha docs: https://developers.google.com/recaptcha/docs/verify
        """
        if response:
            result = json.loads(response.read())
            if result["success"]:
                self.set_bankpassword()
                return
        self.render_page(errors=["Invalid captcha, try again"])


class LogoutHandler(BaseHandler):
    """Log user out of current session"""

    def get(self, *args, **kwargs):
        """Redirect"""
        if self.session is not None:
            self.redirect("/user")
        else:
            self.redirect("/login")

    def post(self, *args, **kwargs):
        """Clears cookies and session data"""
        if self.session is not None:
            user = self.get_current_user()
            EventManager.instance().deauth(user)
            self.session.delete()
        self.clear_all_cookies()
        self.redirect("/")
