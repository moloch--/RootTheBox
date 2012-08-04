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


class FormHandler(RequestHandler):
    ''' This deals with forms, and form validation'''

    def initialize(self):
        #The form object that will be validated agianst
        self.form = None

    def validate_form(self):
        ''' When called, this will check agianst self.form and arguments passed '''
        arguments = self.request.arguments
        results = self.form.validate(arguments)
        return results


class UserBaseHandler(FormHandler):
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

    @authenticated
    def put(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn("%s attempted to use PUT method" % self.request.remote_ip)
        self.render("public/404.html")

    @authenticated
    def delete(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use DELETE method" % self.request.remote_ip)
        self.render("public/404.html")

    @authenticated
    def head(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use HEAD method" % self.request.remote_ip)
        self.render("public/404.html")

    @authenticated
    def options(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use OPTIONS method" % self.request.remote_ip)
        self.render("public/404.html")


class AdminBaseHandler(FormHandler):
    ''' Admin handlers extend this class '''

    def initialize(self, dbsession):
        self.dbsession = dbsession

    @authenticated
    def put(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn("%s attempted to use PUT method" % self.request.remote_ip)
        self.render("public/404.html")

    @authenticated
    def delete(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use DELETE method" % self.request.remote_ip)
        self.render("public/404.html")

    @authenticated
    def head(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use HEAD method" % self.request.remote_ip)
        self.render("public/404.html")

    @authenticated
    def options(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use OPTIONS method" % self.request.remote_ip)
        self.render("public/404.html")
