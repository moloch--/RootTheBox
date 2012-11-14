# -*- coding: utf-8 -*-
'''
Created on Sep 25, 2012

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


from BaseHandlers import BaseHandler
from models import dbsession, User
from libs.Form import Form
from libs.SecurityDecorators import authenticated


class PasswordSecurityHandler(BaseHandler):
    ''' Renders views of items in the market '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Render update hash page '''
        self.render_page()

    @authenticated
    def post(self, *args, **kwargs):
        ''' Attempt to upgrade hash algo '''
        form = Form(
            old_password="Enter your existing password",
            new_password1="Enter a new password",
            new_password2="Confirm your new password",
        )
        user = self.get_current_user()
        if form.validate(self.request.arguments):
            if not user.validate_password(self.get_argument('old_password')):
                self.render_page(["Invalid password"])
            elif not self.get_argument('new_password1') == self.get_argument('new_password2'):
                self.render_page(["New passwords do not match"])
            elif len(self.get_argument('new_password1')) <= self.config.max_password_length:
                self.update_password(self.get_argument('new_password1'))
                self.render_page()
            else:
                self.render_page(["New password is too long"])
        else:
            self.render_page(form.errors)

    def render_page(self, errors=None):
        user = self.get_current_user()
        self.render('upgrades/password_security.html', errors=errors, user=user)

    def update_password(self, new_password):
        ''' Update user to new hashing algorithm '''
        user = self.get_current_user()
        user.algorithm = user.next_algorithm()
        dbsession.add(user)
        dbsession.flush()
        user.password = new_password
        dbsession.add(user)
        dbsession.flush()      