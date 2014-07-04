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


import imghdr
import logging

from uuid import uuid4
from netaddr import IPAddress
from libs.SecurityDecorators import blacklist_ips
from libs.ConfigManager import ConfigManager
from models.Team import Team
from models.Theme import Theme
from models.RegistrationToken import RegistrationToken
from models.GameLevel import GameLevel
from models.User import User, ADMIN_PERMISSION
from handlers.BaseHandlers import BaseHandler
from datetime import datetime


class HomePageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/home.html")


class LoginHandler(BaseHandler):
    ''' Takes care of the login process '''

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.render('public/login.html', errors=None)

    @blacklist_ips
    def post(self, *args, **kwargs):
        ''' Checks submitted username and password '''
        user = User.by_handle(self.get_argument('account', ''))
        password_attempt = self.get_argument('password', '')
        if user is not None and user.validate_password(password_attempt):
            if not user.locked:
                if self.game_started(user):
                    self.successful_login(user)
                    if user.logins == 1 and not user.has_permission(ADMIN_PERMISSION):
                        self.redirect('/user/missions/firstlogin')
                    else:
                        self.redirect('/user')
                else:
                    self.render('public/login.html', errors=["The game has not started yet"])
            else:
                self.render('public/login.html', errors=["Your account has been locked"])
        else:
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
        self.session['theme'] = [str(f) for f in theme.files]
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
                    logging.warning("[BAN HAMMER] Cannot blacklist loopback address")
            except:
                logging.exception("[BAN HAMMER] Exception while attempting to ban ip address")
        self.render('public/login.html', errors=["Bad username and/or password, try again"])


class RegistrationHandler(BaseHandler):
    ''' Registration Code '''

    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.render("public/registration.html", errors=None)

    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        try:
            if self.config.restrict_registration:
                self.check_regtoken()
            team = self.get_team()
            user = self.create_user(team)
            self.render('public/successful_reg.html', account=user.handle)
        except Exception as error:
            logging.exception("Registration got invalid data")
            self.render('public/registration.html', errors=[str(error)])

    def check_regtoken(self):
        regtoken = self.get_argument('token', '')
        token = RegistrationToken.by_value(regtoken)
        if token is not None:
            token.used = True
            self.dbsession.add(token)
            self.dbsession.commit()
        else:
            raise ValueError("Invalid registration token")

    def create_user(self, team):
        ''' Add user to the database '''
        if self.get_argument('pass1', '') != self.get_argument('pass2', ''):
            raise ValueError("Passwords do not match")
        user = User()
        user.handle = self.get_argument('handle', '')
        user.password = self.get_argument('pass1', '')
        user.bank_password = self.get_argument('bpass', '')
        team.members.append(user)
        self.dbsession.add(user)
        self.dbsession.add(team)
        self.dbsession.commit()
        event = self.event_manager.create_joined_team_event(user)
        self.new_events.append(event)
        return user

    def get_team(self):
        ''' Create a team object, or pull the existing one '''
        team = Team.by_uuid(self.get_argument('team', ''))
        if team is not None and self.config.max_team_size <= len(team.members):
            raise ValueError("Team %s is already full" % team.name)
        return team if team is not None else self.create_team()

    def create_team(self):
        ''' Create a new team '''
        if self.config.public_teams:
            team = Team()
            team.name = self.get_argument('team_name', '')
            team.motto = self.get_argument('motto', '')
            level_0 = GameLevel.all()[0]
            team.game_levels.append(level_0)
            return team
        else:
            raise ValueError("Public teams are not enabled")


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
