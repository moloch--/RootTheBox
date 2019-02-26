# -*- coding: utf-8 -*-
'''
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

This file holds publically exposed handlers (handlers that to not require
any authentication) with the exception of error handlers and the scoreboard

'''


import logging

from netaddr import IPAddress
from libs.SecurityDecorators import blacklist_ips
from libs.ValidationError import ValidationError
from libs.StringCoding import unicode3
from models.Team import Team
from models.Theme import Theme
from models.RegistrationToken import RegistrationToken
from models.GameLevel import GameLevel
from models.User import User, ADMIN_PERMISSION
from handlers.BaseHandlers import BaseHandler
from datetime import datetime
from pbkdf2 import PBKDF2
from tornado.options import options

class HomePageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the main page '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.render("public/home.html")


class LoginHandler(BaseHandler):

    ''' Takes care of the login process '''

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.render('public/login.html', info=None, errors=None)

    @blacklist_ips
    def post(self, *args, **kwargs):
        ''' Checks submitted username and password '''
        user = User.by_handle(self.get_argument('account', ''))
        password_attempt = self.get_argument('password', '')
        if user is not None:
            if user.validate_password(password_attempt):
                if not user.locked:
                    if self.game_started(user):
                        self.successful_login(user)
                        if self.config.story_mode and user.logins == 1 and not user.has_permission(ADMIN_PERMISSION):
                            self.redirect('/user/missions/firstlogin')
                        else:
                            self.redirect('/user')
                    else:
                        self.render('public/login.html',
                                    errors=None, info=["The game has not started yet"])
                else:
                    self.render('public/login.html',
                                info=None, errors=["Your account has been locked"])
            else:
                self.failed_login()
        else:
            if password_attempt is not None:
                PBKDF2.crypt(password_attempt, "BurnTheHashTime")
            self.failed_login()

    def game_started(self, user):
        if self.application.settings['game_started']:
            return True
        else:
            return True if user.has_permission(ADMIN_PERMISSION) else False

    def successful_login(self, user):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %s from %s" % (
            user.handle, self.request.remote_ip,
        ))
        user.last_login = datetime.now()
        user.logins += 1
        self.dbsession.add(user)
        self.dbsession.commit()
        self.start_session()
        theme = Theme.by_id(user.theme_id)
        if user.team is not None:
            self.session['team_id'] = int(user.team.id)
        self.session['user_id'] = int(user.id)
        self.session['user_uuid'] = user.uuid
        self.session['handle'] = user.handle
        self.session['theme'] = [unicode3(f) for f in theme.files]
        self.session['theme_id'] = int(theme.id)
        if user.has_permission(ADMIN_PERMISSION):
            self.session['menu'] = 'admin'
        else:
            self.session['menu'] = 'user'
        self.session.save()

    def failed_login(self):
        ''' Called if username/password is invalid '''
        ip = self.request.remote_ip
        logging.info("[BAN HAMMER] Failed login attempt from: %s" % ip)
        failed_logins = self.application.settings['failed_logins']
        if ip in failed_logins:
            failed_logins[ip] += 1
        else:
            failed_logins[ip] = 1
        threshold = self.application.settings['blacklist_threshold']
        if self.application.settings['automatic_ban'] and threshold <= failed_logins[ip]:
            logging.info("[BAN HAMMER] Automatically banned IP: %s" % ip)
            try:
                if not IPAddress(ip).is_loopback():
                    self.application.settings['blacklisted_ips'].append(ip)
                else:
                    logging.warning(
                        "[BAN HAMMER] Cannot blacklist loopback address")
            except:
                logging.exception("Error while attempting to ban ip address")
        self.render('public/login.html',
                    info=None, errors=["Bad username and/or password, try again"])


class RegistrationHandler(BaseHandler):

    ''' Registration Code '''

    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.render("public/registration.html", errors=None, suspend=self.application.settings['suspend_registration'])

    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        try:
            if self.application.settings['suspend_registration']:
                self.render('public/registration.html', errors=None, suspend=True)
            else:
                if self.config.restrict_registration:
                    self.check_regtoken()
                user = self.create_user()
                self.render('public/successful_reg.html', account=user.handle)
        except ValidationError as error:
            self.render('public/registration.html', errors=[unicode3(error)], suspend=self.application.settings['suspend_registration'])

    def check_regtoken(self):
        regtoken = self.get_argument('token', '')
        token = RegistrationToken.by_value(regtoken)
        if token is not None and not token.used:
            token.used = True
            self.dbsession.add(token)
            self.dbsession.commit()
        else:
            raise ValidationError("Invalid registration token")

    def create_user(self):
        ''' Add user to the database '''
        if User.by_handle(self.get_argument('handle', '')) is not None:
            raise ValidationError("This hacker name is already registered")
        if self.get_argument('pass1', '') != self.get_argument('pass2', ''):
            raise ValidationError("Passwords do not match")
        user = User()
        user.handle = self.get_argument('handle', '')
        user.password = self.get_argument('pass1', '')
        user.bank_password = self.get_argument('bpass', '')
        user.name = self.get_argument('playername', '')
        user.email = self.get_argument('email','')
        team = self.get_team()
        self.dbsession.add(user)
        self.dbsession.add(team)
        self.dbsession.commit()

         # Avatar
        avatar_select = self.get_argument('user_avatar_select', '')
        if avatar_select and len(avatar_select) > 0:
            user._avatar = avatar_select
        elif hasattr(self.request, 'files') and 'avatar' in self.request.files:
            user.avatar = self.request.files['avatar'][0]['body']
        team.members.append(user)
        if not options.teams:
            if avatar_select and len(avatar_select) > 0:
                team._avatar = avatar_select
            elif hasattr(self.request, 'files') and 'avatar' in self.request.files:
                team.avatar = self.request.files['avatar'][0]['body']  
        self.dbsession.add(user)
        self.dbsession.add(team)
        self.dbsession.commit()  
        self.event_manager.user_joined_team(user)
        return user

    def get_team(self):
        ''' Create a team object, or pull the existing one '''
        team = Team.by_uuid(self.get_argument('team', ''))
        code = self.get_argument('team-code', '')
        if team is not None and self.config.max_team_size <= len(team.members):
            raise ValidationError("Team %s is already full" % team.name)
        elif team is not None and team.code != code:
            raise ValidationError("Invalid team code for %s" % team.name)
        return team if team is not None else self.create_team()

    def create_team(self):
        ''' Create a new team '''
        if not self.config.teams:
            team = Team.by_name(self.get_argument('handle', ''))
            if team is None:
                team = Team()
                team.name = self.get_argument('handle', '')
            else:
                logging.info("Team %s already exists - Player Mode: reset team." % team.name)
                team.flags = []
                team.hints = []
                team.boxes = []
                team.items = []
                team.game_levels = []
                team.purchased_source_code = []
            team.motto = self.get_argument('motto', '')
            if self.config.banking:
                team.money = self.config.starting_team_money
            else:
                team.money = 0
            level_0 = GameLevel.by_number(0)
            if not level_0:
                level_0 = GameLevel.all()[0]
            team.game_levels.append(level_0)
            return team
        elif self.config.public_teams:
            if Team.by_name(self.get_argument('team_name', '')) is not None:
                raise ValidationError("This team name is already registered")
            team = Team()
            team.name = self.get_argument('team_name', '')
            team.motto = self.get_argument('motto', '')
            if not self.config.banking:
                team.money = 0
            level_0 = GameLevel.by_number(0)
            if not level_0:
                level_0 = GameLevel.all()[0]
            team.game_levels.append(level_0)
            return team
        else:
            raise ValidationError("Public teams are not enabled")


class FakeRobotsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        '''
        Troll time :P - TODO: Add BeEF to these pages
        '''
        self.set_header('Content-Type', 'text/plain')
        self.write('# Block access to admin stuff\n\n')
        self.write('User-agent: *\n\n')
        self.write('/admin/create/sql_query\n')
        self.write('/admin/create/flag_capture\n')
        self.write('/admin/view/db_users.txt\n')
        self.write('/admin/view/passwords.txt\n')
        self.write('/admin/manager/c99.php\n')
        self.finish()


class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('public/about.html')
