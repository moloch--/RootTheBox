# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

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

from models import User
from libs.SecurityDecorators import *
from libs.Session import SessionManager
from tornado.web import RequestHandler


class UserBaseHandler(RequestHandler):
    ''' User handlers extend this class '''

    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.session_manager = SessionManager.Instance()
        self.session = self.session_manager.get_session(
            self.get_secure_cookie('auth'), self.request.remote_ip)

    def get_current_user(self):
        if self.session != None:
            return User.by_user_name(self.session.data['user_name'])
        return None


class AdminBaseHandler(RequestHandler):
    ''' Admin handlers extend this class '''

    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.get_functions = {
            'challenge': self.get_challenge,
            'action': self.get_action,
            'team': self.get_team,
            'user': self.get_user,
            'box': self.get_box,
            'crackme': self.get_crack_me,
            'se': self.get_se
        }
        self.post_functions = {
            'challenge': self.post_challenge,
            'action': self.post_action,
            'team': self.post_team,
            'user': self.post_user,
            'box': self.post_box,
            'crackme': self.post_crack_me,
            'se': self.post_se
        }

    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        if len(args) == 1 and args[0] in self.get_functions.keys():
            self.get_functions[args[0]](*args, **kwargs)
        elif 1 <= len(args):
            self.render("admin/unknown_object.html", unknown_object=args[0])
        else:
            self.render("admin/errror.html", errors="Missing parameters")

    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        if len(args) == 1 and args[0] in self.post_functions.keys():
            self.post_functions[args[0]](*args, **kwargs)
        elif 1 <= len(args):
            self.render("admin/unknown_object.html", unknown_object=args[0])
        else:
            self.render("admin/error.html", errors="Missing parameters")
