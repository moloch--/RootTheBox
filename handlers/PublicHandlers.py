# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

@author: moloch

    Copyright [2012] [Redacted Labs]

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

from models.User import User
from libs.Form import Form
from libs.Session import SessionManager
from tornado.web import RequestHandler
from recaptcha.client import captcha
from string import ascii_letters, digits


class HomePageHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/home.html")


class LoginHandler(RequestHandler):
    ''' Takes care of the login process '''

    def initialize(self):
        self.form = Form(
            account="Enter an account name",
            password="A password is required to login",
        )

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render('public/login.html', errors=None)

    def post(self, *args, **kwargs):
        ''' Checks submitted username and password '''
        if self.form.validate(self.request.arguments):
            user = User.by_account(self.request.arguments['account'])
            if user != None and user.validate_password(password):
                if user.team == None and not user.has_permission('admin'):
                    # Successful login, but not assigned to a team yet
                    self.render("public/login.html", errors=["You must be assigned to a team before you can login"])
                else:
                    self.successful_login()
                    self.redirect('/user')
            else:
                self.failed_login()
        else:
            self.render('public/login.html', errors=self.form.errors)

    def successful_login(self):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %s/%s from %s" % (user.account, user.handle, self.request.remote_ip))
        session_manager = SessionManager.Instance()
        sid, session = session_manager.start_session()
        self.set_secure_cookie(name='auth', value=str(sid), expires_days=1, HttpOnly=True)
        session.data['handle'] = str(user.handle)
        session.data['ip'] = str(self.request.remote_ip)
        if user.has_permission('admin'):
            session.data['menu'] = 'admin'
        else:
            session.data['menu'] = 'user'

    def failed_login(self):
        ''' Called if username or password is invalid '''
        logging.info("Failed login attempt from %s " % self.request.remote_ip)
        self.render('public/login.html', errors=["Bad username and/or password, try again"])


class UserRegistraionHandler(RequestHandler):

    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.form = Form(
            account="Please enter an account name",
            handle="Please enter a handle",
            pass1="Please enter a password",
            pass2="Please confirm your password",
            token="Please enter a registration token"
        )

    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render("public/registration.html", errors=None)

    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        # Check user_name parameter
        if self.form.validate(self.request.arguments):
            if User.by_account(self.request.arguments['account']) != None:
                self.render('public/registration.html',
                            errors=['Account name already taken'])
            elif self.request.arguments['account'] == self.request.arguments['handle']:
                self.render('public/registration.html',
                            errors=['Account name and hacker name must differ'])
            elif User.by_handle(self.request.arguments['handle']) != None:
                self.render(
                    'public/registration.html', errors=['Handle already taken'])
            elif not self.request.arguments['pass1'] == self.request.arguments['pass2']:
                self.render(
                    'public/registration.html', errors=['Passwords do not match'])
            elif not 0 < len(self.request.arguments['pass1']) <= config.max_password_length:
                self.render('public/registration.html',
                            errors=['Password must be 1-%d characters' % config.max_password_length])
            else:
                user = User(
                    account=unicode(account),
                    handle=unicode(handle),
                    password=password
                )
                self.dbsession.add(user)
                self.dbsession.flush()
            self.redirect('/login')
        elif 0 < len(self.form.errors):
            self.render('public/registration.html', errors=self.form.errors)
        else:
            self.render('public/registration.html', errors=['Unknown error'])


class AboutHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('public/about.html')