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
'''


import logging

from libs.Form import Form
from libs.SecurityDecorators import debug
from libs.ConfigManager import ConfigManager
from handlers.BaseHandlers import BaseHandler
from tornado.web import RequestHandler
from recaptcha.client import captcha
from string import ascii_letters, digits
from models import dbsession, User, Team, Theme, RegistrationToken


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
            user = User.by_account(self.request.arguments['account'][0])
            if user != None and user.validate_password(self.request.arguments['password'][0]):
                self.successful_login(user)
                self.redirect('/user')
            else:
                self.failed_login()
        else:
            self.render('public/login.html', errors=self.form.errors)

    @debug
    def successful_login(self, user):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %s/%s from %s" % (user.account, user.handle, self.request.remote_ip,))
        self.start_session()
        theme = Theme.by_id(user.theme_id)
        self.session['team_id'] = int(user.team.id)
        self.session['user_id'] = int(user.id)
        self.session['handle'] = ''.join(user.handle) # Copy string
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
        self.render('public/login.html', errors=[
            "Bad username and/or password, try again"])


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
            if User.by_account(self.get_argument('account')) != None:
                self.render('public/registration.html',
                            errors=['Account name already taken'])
            elif self.request.arguments['account'] == self.request.arguments['handle']:
                self.render('public/registration.html',
                            errors=['Account name and hacker name must differ'])
            elif User.by_handle(self.get_argument('handle')) != None:
                self.render(
                    'public/registration.html', errors=['Handle already taken'])
            elif not self.request.arguments['pass1'] == self.request.arguments['pass2']:
                self.render(
                    'public/registration.html', errors=['Passwords do not match'])
            elif not 0 < len(self.request.arguments['pass1']) <= config.max_password_length:
                self.render('public/registration.html',
                            errors=['Password must be 1-%d characters' % config.max_password_length])
            elif len(self.get_argument('team')) == 0 or Team.by_uuid(self.get_argument('team')) == None:
                self.render('public/registration.html', errors=["Please select a team to join"])
            elif RegistrationToken.by_value(self.get_argument('token').lower()) == None and config.debug == False:
                self.render('public/registration.html', errors=["Invalid registration token"])
            else:
                self.create_user()
                self.redirect('/login')
        else:
            self.render('public/registration.html',
                        errors=form.errors)

    @debug
    def create_user(self):
        ''' Add user to the database '''
        team = Team.by_uuid(self.get_argument('team'))
        user = User(
            account=unicode(self.get_argument('account')),
            handle=unicode(self.get_argument('handle')),
            team_id=team.id,
        )
        dbsession.add(user)
        dbsession.flush()
        user.password = self.get_argument('pass1')
        token = RegistrationToken.by_value(self.get_argument('token').lower())
        if token != None: # May be None if debug mode is on
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
        if self.session != None:
            self.session.delete()
        self.clear_all_cookies()
        self.redirect("/")
