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
from libs.SecurityDecorators import debug
from libs.ConfigManager import ConfigManager
from handlers.BaseHandlers import BaseHandler
from models import dbsession, User, Team, Theme, \
    RegistrationToken


class HomePageHandler(BaseHandler):

    @debug
    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/home.html")


class LoginHandler(BaseHandler):
    ''' Takes care of the login process '''

    @debug
    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render('public/login.html', errors=None)

    @debug
    def post(self, *args, **kwargs):
        ''' Checks submitted username and password '''
        form = Form(
            account="Enter an account name",
            password="A password is required to login",
        )
        if form.validate(self.request.arguments):
            user = User.by_account(self.get_argument('account'))
            password_attempt = self.get_argument('password')
            if user is not None and user.validate_password(password_attempt):
                self.successful_login(user)
                self.redirect('/user')
            else:
                self.failed_login()
        else:
            self.render('public/login.html', errors=form.errors)

    @debug
    def successful_login(self, user):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %r/%r from %s" %
            (user.account, user.handle, self.request.remote_ip,))
        self.start_session()
        theme = Theme.by_id(user.theme_id)
        if user.team is not None:
            self.session['team_id'] = int(user.team.id)
        self.session['user_id'] = int(user.id)
        self.session['handle'] = ''.join(user.handle)  # Copy string
        self.session['theme'] = ''.join(theme.cssfile)
        if user.has_permission('admin'):
            self.session['menu'] = 'admin'
        else:
            self.session['menu'] = 'user'
        self.session.save()

    @debug
    def failed_login(self):
        ''' Called if username or password is invalid '''
        logging.info("Failed login attempt from: %s" % self.request.remote_ip)
        self.render('public/login.html',
            errors=["Bad username and/or password, try again"]
        )


class UserRegistrationHandler(BaseHandler):
    ''' Registration Code '''

    @debug
    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render(
            "public/registration.html", errors=None)

    @debug
    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        form = Form(
            account="Please enter an account name",
            handle="Please enter a handle",
            team="Please select a team to join",
            pass1="Please enter a password",
            pass2="Please confirm your password",
            token="Please enter a registration token"
        )
        if form.validate(self.request.arguments):
            config = ConfigManager.Instance()
            account = self.get_argument('account').lower()
            handle = self.get_argument('handle').lower()
            rtok = self.get_argument('token', '__none__').lower()
            passwd = self.get_argument('pass1')
            if User.by_account(account) is not None:
                self.render('public/registration.html',
                    errors=['Account name already taken']
                )
            elif account == handle:
                self.render('public/registration.html',
                    errors=['Account name and hacker name must differ']
                )
            elif User.by_handle(handle) is not None:
                self.render('public/registration.html',
                    errors=['Handle already taken']
                )
            elif not passwd == self.get_argument('pass2'):
                self.render('public/registration.html',
                    errors=['Passwords do not match']
                )
            elif not 0 < len(passwd) <= config.max_password_length:
                self.render('public/registration.html',
                    errors=['Password must be 1-%d characters'
                                % config.max_password_length]
                )
            elif Team.by_uuid(self.get_argument('team', '')) is None:
                self.render('public/registration.html',
                    errors=["Please select a team to join"]
                )
            elif RegistrationToken.by_value(rtok) is None and not config.debug:
                self.render('public/registration.html',
                    errors=["Invalid registration token"]
                )
            else:
                self.create_user(account, handle, passwd, rtok)
                self.redirect('/login')
        else:
            self.render('public/registration.html', errors=form.errors)

    @debug
    def create_user(self, account, handle, passwd, rtok):
        ''' Add user to the database '''
        team = Team.by_uuid(self.get_argument('team', ''))
        user = User(
            account=unicode(account),
            handle=unicode(handle),
            team_id=team.id,
        )
        dbsession.add(user)
        dbsession.flush()
        user.password = passwd
        token = RegistrationToken.by_value(rtok)
        if token is not None:  # May be None if debug mode is on
            token.used = True
            dbsession.add(token)
        dbsession.add(user)
        dbsession.flush()
        self.event_manager.joined_team(user)


class AboutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('public/about.html')


class LogoutHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Clears cookies and session data '''
        if self.session is not None:
            self.session.delete()
        self.clear_all_cookies()
        self.redirect("/")
