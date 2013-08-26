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

from libs.Form import Form
from libs.ConfigManager import ConfigManager
from models import dbsession, User, Team, Theme, RegistrationToken, GameLevel
from models.User import ADMIN_PERMISSION
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

    def post(self, *args, **kwargs):
        ''' Checks submitted username and password '''
        form = Form(
            account="Enter an account name",
            password="A password is required to login",
        )
        if form.validate(self.request.arguments):
            user = User.by_handle(self.get_argument('account'))
            password_attempt = self.get_argument('password')
            if user is not None and user.validate_password(password_attempt):
                if not user.locked:
                    self.successful_login(user)
                    if 1 == user.logins and not user.has_permission(ADMIN_PERMISSION):
                        self.redirect('/user/missions/firstlogin')
                    else:
                        self.redirect('/user')
                else:
                    self.render('public/login.html', 
                        errors=["Your account has been locked"]
                    )
            else:
                self.failed_login()
        else:
            self.render('public/login.html', errors=form.errors)

    def successful_login(self, user):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %s from %s" % (
            user.handle, self.request.remote_ip,
        ))
        user.last_login = datetime.now()
        user.logins += 1
        dbsession.add(user)
        dbsession.flush()
        self.start_session()
        theme = Theme.by_id(user.theme_id)
        if user.team is not None:
            self.session['team_id'] = int(user.team.id)
        self.session['user_id'] = int(user.id)
        self.session['user_uuid'] = user.uuid
        self.session['handle'] = user.handle
        self.session['theme'] = theme.cssfile
        if user.has_permission(ADMIN_PERMISSION):
            self.session['menu'] = 'admin'
        else:
            self.session['menu'] = 'user'
        self.session.save()

    def failed_login(self):
        ''' Called if username or password is invalid '''
        logging.info("Failed login attempt from: %s" % self.request.remote_ip)
        self.render('public/login.html',
            errors=["Bad username and/or password, try again"]
        )


class RegistrationHandler(BaseHandler):
    ''' Registration Code '''

    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.render("public/registration.html", 
                errors=None
            )

    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        form = Form(
            handle="Please enter a handle",
            pass1="Please enter a password",
            pass2="Please confirm your password",
            bpass1="Please enter a bank account password",
        )
        if form.validate(self.request.arguments):
            errors = []
            errors += self.validate_user()
            errors += self.validate_team()
            if 0 == len(errors):
                team = self.get_team()
                user = self.create_user(team)
                self.render('public/successful_reg.html', account=user.handle)
            else:
                self.render('public/registration.html', errors=errors)
        else:
            self.render('public/registration.html', errors=form.errors)

    def validate_user(self):
        ''' Validate user arguments '''
        errors = []
        handle = self.get_argument('handle')
        rtok = self.get_argument('token', '')
        passwd = self.get_argument('pass1', '')
        bank_passwd = self.get_argument('bpass1', '')
        if not 2 < len(handle) < 16:
            errors.append('Hacker name must be 3-15 characters')
        elif User.by_handle(handle) is not None:
            errors.append('Handle already taken')
        elif not passwd == self.get_argument('pass2'):
            errors.append('Passwords do not match')
        elif len(passwd) < 16 and not self.config.debug:
            errors.append('Password must be at least 16 characters')
        elif not 0 < len(bank_passwd) <= self.config.max_password_length:
            errors.append(
                'Bank account password must be 1-%d characters' % self.config.max_password_length
            )
        elif RegistrationToken.by_value(rtok) is None and self.config.restrict_registration:
            errors.append("Invalid registration token")
        return errors

    def validate_team(self):
        ''' Validate team arguments '''
        errors = []
        join_team = self.get_argument('team', '')
        if Team.by_uuid(join_team) is None:
            if self.config.public_teams:
                team_name = self.get_argument('team_name', '')
                motto = self.get_argument('motto', '')
                if 2 < len(team_name) < 15:
                    if Team.by_name(team_name) is not None:
                        errors.append("A team with that name already exists")
                else:
                    errors.append('Team name must be 3 - 15 characters')
                if not 2 < len(motto):
                    errors.append('Team motto must be more than 3 characters')  
                return errors
            else:
                return ["You must select a team to join"]
        else:
            return []

    def create_user(self, team):
        ''' Add user to the database '''
        handle = self.get_argument('handle')
        user = User(
            handle=unicode(handle),
            team_id=team.id,
        )
        dbsession.add(user)
        dbsession.flush()
        user.password = self.get_argument('pass1', '')
        user.bank_password = self.get_argument('bpass1', '')
        if self.config.restrict_registration:
            rtok = self.get_argument('token', '')
            token = RegistrationToken.by_value(rtok)
            dbsession.add(token)
        dbsession.add(user)
        dbsession.flush()
        event = self.event_manager.create_joined_team_event(user)
        self.new_events.append(event)
        return user

    def get_team(self):
        ''' Create a team object, or pull the existing one '''
        team = Team.by_uuid(self.get_argument('team', ''))
        return team if team is not None else self.create_team()

    def create_team(self):
        ''' Create a new team '''
        assert self.config.public_teams
        team = Team(
            name=unicode(self.get_argument('team_name')),
            motto=unicode(self.get_argument('motto')),
        )
        level_0 = GameLevel.all()[0]
        team.game_levels.append(level_0)
        dbsession.add(team)
        dbsession.flush()
        return team


class FakeRobotsHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Troll time '''
        self.set_header('Content-Type', 'text/plain')
        self.write('# Block access to admin stuff\n\n')
        self.write('User-agent: *\n\n')
        self.write('/admin/create/sql_query\n')
        self.write('/admin/create/flag_capture\n')
        self.write('/admin/view/db_users.txt\n')
        self.write('/admin/view/passwords.txt\n')
        self.finish()


class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('public/about.html')
