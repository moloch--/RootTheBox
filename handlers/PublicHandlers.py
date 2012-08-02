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

    def get(self, *args, **kwargs):
        ''' Display the login page '''
        self.render(
            'public/login.html', message='User authentication required')

    def post(self, *args, **kwargs):
        ''' Checks submitted username and password '''
        try:
            username = self.get_argument('username')
            user = User.by_name(username)
        except:
            self.render(
                'public/login.html', message="Type in an account name")
            return
        try:
            password = self.get_argument('password')
        except:
            self.render('public/login.html', message="Type in a password")
            return
        if user != None and user.validate_password(password):
            if user.team == None and not user.has_permission('admin'):
                # Successful login, but not assigned to a team yet
                self.render("public/login.html", message="You must be assigned to a team before you can login")
            else:
                self.successful_login()
                self.redirect('/user')
        else:
            self.failed_login()

    def successful_login(self):
        ''' Called when a user successfully logs in '''
        logging.info("Successful login: %s from %s" % (user.user_name, self.request.remote_ip))
        session_manager = SessionManager.Instance()
        sid, session = session_manager.start_session()
        self.set_secure_cookie(name='auth', value=str(sid), expires_days=1, HttpOnly=True)
        session.data['user_name'] = str(user.user_name)
        session.data['ip'] = str(self.request.remote_ip)
        if user.has_permission('admin'):
            session.data['menu'] = str('admin')
        else:
            session.data['menu'] = str('user')

    def failed_login(self):
        ''' Called if username or password is invalid '''
        logging.info("Failed login attempt from %s " % self.request.remote_ip)
        self.render('public/login.html', message="Bad username and/or password, try again")



class UserRegistraionHandler(RequestHandler):

    def initialize(self, dbsession):
        self.dbsession = dbsession

    def get(self, *args, **kwargs):
        ''' Renders the registration page '''
        self.render("public/registration.html",
                    errors='Please fill out the form below')

    def post(self, *args, **kwargs):
        ''' Attempts to create an account, with shitty form validation '''
        # Check user_name parameter
        try:
            user_name = self.get_argument('username')
        except:
            self.render('public/registration.html',
                        errors='Please enter a valid account name')
            return
        # Check handle parameter
        try:
            handle = self.get_argument('handle')
        except:
            self.render('public/registration.html',
                        errors='Please enter a valid handle')
            return
        # Check password parameter
        try:
            password1 = self.get_argument('pass1')
            password2 = self.get_argument('pass2')
            if password1 != password2:
                self.render('public/registration.html',
                            errors='Passwords did not match')
            else:
                password = password1
        except:
            self.render('public/registration.html',
                        errors='Please enter a password')
            return
        # Create account
        if User.by_name(user_name) != None:
            self.render('public/registration.html',
                        errors='Account name already taken')
        elif user_name == handle:
            self.render('public/registration.html',
                        errors='Account name and hacker name must differ')
        elif User.by_display_name(handle) != None:
            self.render(
                'public/registration.html', errors='Handle already taken')
        elif not 0 < len(password) <= config.max_password_length:
            self.render('public/registration.html',
                        errors='Password must be 1-%d characters' % config.max_password_length)
        elif not response.is_valid:
            self.render(
                'public/registration.html', errors='Invalid Recaptcha!')
        else:
            char_white_list = ascii_letters + digits + " _-()"
            user_name = filter(lambda char: char in char_white_list, user_name)
            display_name = filter(lambda char: char in char_white_list, handle)
            user = User(
                name=unicode(user_name),
                display_name=unicode(display_name),
                password=password
            )
            self.dbsession.add(user)
            self.dbsession.flush()
        self.redirect('/login')


class AboutHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Renders the about page '''
        self.render('public/about.html')