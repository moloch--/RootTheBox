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
from models.Team import Team
from libs.Form import Form
from libs.ConfigManager import ConfigManager
from libs.Session import SessionManager
from handlers.BaseHandlers import BaseHandler
from tornado.web import RequestHandler
from recaptcha.client import captcha
from string import ascii_letters, digits


class HomePageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render("public/home.html")


class LoginHandler(BaseHandler):
    ''' Takes care of the login process '''

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render('public/login.html', errors=None)

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

    def successful_login(self, user):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %s/%s from %s" % (user.
                                                          account, user.handle, self.request.remote_ip))
        self.start_session()
        self.session['handle'] = ''.join(user.handle) # Don't leave a ref to user object
        self.session['theme_id'] = user.theme_id
        if user.has_permission('admin'):
            self.session['menu'] = 'admin'
        else:
            self.session['menu'] = 'user'
        self.session.save()

    def failed_login(self):
        ''' Called if username or password is invalid '''
        logging.info("Failed login attempt from %s " % self.request.remote_ip)
        self.render('public/login.html', errors=[
            "Bad username and/or password, try again"])


class UserRegistraionHandler(BaseHandler):
    ''' Registration Code '''

    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render(
            "public/registration.html", errors=None)

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
            elif len(self.request.arguments['team'][0]) == 0 or Team.by_uuid(self.request.arguments['team'][0]) == None:
                self.render('public/registration.html', errors=[
                    "Please select a team to join"], teams=Team.get_all())
            else:
                team = Team.by_uuid(self.request.arguments['team'][0])
                user = User(
                    account=unicode(self.request.arguments['account']),
                    handle=unicode(self.request.arguments['handle']),
                    team_id=team.id,
                    password=str(self.request.arguments['pass1'][0]),
                )
                self.dbsession.add(user)
                self.dbsession.flush()
            self.redirect('/login')
        elif 0 < len(self.form.errors):
            self.render('public/registration.html',
                        errors=self.form.errors)
        else:
            self.render('public/registration.html', errors=[
                'Unknown error'])


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
