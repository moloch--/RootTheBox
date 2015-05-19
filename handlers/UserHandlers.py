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

This file contains code for managing user accounts

'''


import urllib
import logging
import tornado

from models.User import User, ADMIN_PERMISSION
from models.Theme import Theme
from libs.EventManager import EventManager
from libs.ValidationError import ValidationError
from libs.SecurityDecorators import authenticated
from BaseHandlers import BaseHandler
from tornado.options import options


RECAPTCHA_URL = 'http://www.google.com/recaptcha/api/verify'


class HomeHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Display the default user page '''
        user = self.get_current_user()
        if user.has_permission(ADMIN_PERMISSION):
            self.render('admin/home.html', user=user)
        else:
            self.render('user/home.html', user=user)


class SettingsHandler(BaseHandler):
    ''' Modify user controlled attributes '''

    @authenticated
    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        ''' Display the user settings '''
        self.render_page()

    @authenticated
    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        ''' Calls function based on parameter '''
        post_functions = {
            'avatar': self.post_avatar,
            'password': self.post_password,
            'bank_password': self.post_bankpassword,
            'theme': self.post_theme,
        }
        if len(args) == 1 and args[0] in post_functions:
            post_functions[args[0]]()
        else:
            self.render_page()

    def render_page(self, errors=[], success=[]):
        ''' Small wrap for self.render to cut down on lenghty params '''
        self.add_content_policy('script', "'unsafe-eval'")
        current_theme = Theme.by_id(self.session["theme_id"])
        self.add_content_policy('script', 'www.google.com')
        self.add_content_policy('img', 'www.google.com')
        self.render("user/settings.html",
                    errors=errors,
                    success=success,
                    current_theme=current_theme)

    def post_avatar(self, *args, **kwargs):
        '''
        Saves avatar - Reads file header an only allows approved formats
        '''
        user = self.get_current_user()
        if hasattr(self.request, 'files') and 'avatar' in self.request.files:
            try:
                user.avatar = self.request.files['avatar'][0]['body']
                self.dbsession.add(user)
                self.dbsession.commit()
                self.render_page(success=["Updated avatar"])
            except ValidationError as error:
                self.render_page(errors=[str(error), ])
        else:
            self.render_page(errors=["Please provide an image"])

    def post_theme(self, *args, **kwargs):
        ''' Change per-user theme '''
        theme = Theme.by_uuid(self.get_argument('theme_uuid', ''))
        if theme is not None:
            self.session['theme_id'] = theme.id
            self.session['theme'] = [str(f) for f in theme.files]
            self.session.save()
            user = self.get_current_user()
            user.theme_id = theme.id
            self.dbsession.add(user)
            self.dbsession.commit()
            self.render_page()
        else:
            self.render_page(errors=["Theme does not exist."])

    def post_password(self, *args, **kwargs):
        ''' Called on POST request for password change '''
        self.set_password(
            self.get_current_user(),
            self.get_argument('old_password'),
            self.get_argument('new_password'),
            self.get_argument('new_password2')
        )

    def set_password(self, user, old_password, new_password, new_password2):
        ''' Sets a users password '''
        if user.validate_password(old_password):
             if len(new_password) >= options.min_user_password_length or self.config.debug:
                if 16 <= len(new_password) or self.config.debug:
                    user.password = new_password
                    self.dbsession.add(user)
                    self.dbsession.commit()
                    self.render_page(success=["Successfully updated password"])
                else:
                    self.render_page(errors=["Password must be at least %d characters " % (
                        options.min_user_password_length,
                    )])
             else:
                self.render_page(errors=["New password's didn't match"])
        else:
            self.render_page(errors=["Invalid old password"])

    def post_bankpassword(self):
        ''' Update user's bank password '''
        old_bankpw = self.get_argument('old_bpassword')
        user = self.get_current_user()
        if user.validate_bank_password(old_bankpw):
            if self.config.recaptcha_enabled:
                self.verify_recaptcha()
            else:
                self.set_bankpassword()
        else:
            self.render_page(errors=["Invalid old password."])

    def set_bankpassword(self):
        user = self.get_current_user()
        user.bank_password = self.get_argument('new_bpassword')
        self.dbsession.add(user)
        self.dbsession.commit()
        self.render_page(success=['Successfully updated bank password'])

    def verify_recaptcha(self):
        ''' Checks recaptcha '''
        recaptcha_challenge = self.get_argument('recaptcha_challenge_field', '')
        recaptcha_response = self.get_argument('recaptcha_response_field', '')
        recaptcha_req_data = {
            'privatekey': self.config.recaptcha_private_key,
            'remoteip': self.request.remote_ip,
            'challenge': recaptcha_challenge,
            'response': recaptcha_response
        }
        try:
            recaptcha_http = tornado.httpclient.AsyncHTTPClient()
            recaptcha_req_body = urllib.urlencode(recaptcha_req_data)
            recaptcha_http.fetch(RECAPTCHA_URL, self.recaptcha_callback,
                                 method='POST',
                                 body=recaptcha_req_body)
        except tornado.httpclient.HTTPError:
            logging.exception('Recaptcha AsyncHTTP request threw an exception')
            self.recaptcha_callback(None)
            self.render_page(errors=['Error making backend recaptcha request'])

    def recaptcha_callback(self, response):
        '''
        Validates recaptcha response
        Recaptcha docs: https://developers.google.com/recaptcha/docs/verify
        '''
        if response and response.body.startswith('true'):
            self.set_bankpassword()
        else:
            self.render_page(errors=["Invalid captcha, try again"])


class LogoutHandler(BaseHandler):
    ''' Log user out of current session '''

    def get(self, *args, **kwargs):
        ''' Redirect '''
        if self.session is not None:
            self.redirect('/user')
        else:
            self.redirect('/login')

    def post(self, *args, **kwargs):
        ''' Clears cookies and session data '''
        if self.session is not None:
            user = self.get_current_user()
            EventManager.instance().deauth(user)
            self.session.delete()
        self.clear_all_cookies()
        self.redirect("/")
