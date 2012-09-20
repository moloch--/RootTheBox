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


import imghdr
import base64
import logging

from os import path
from uuid import uuid1
from random import randint
from base64 import b64encode
from mimetypes import guess_type
from libs.Form import Form
from libs.SecurityDecorators import *
from libs.WebSocketManager import WebSocketManager
from libs.Notification import Notification
from models import Team, Box
from handlers.BaseHandlers import BaseHandler
from tornado.web import RequestHandler
from string import ascii_letters, digits


class AdminCreateHandler(BaseHandler):
    ''' Handler used to create game objects '''

    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Renders Corp/Box/Flag create pages '''
        self.game_objects = {
            'corporation': 'admin/create/corporation.html',
            'box': 'admin/create/box.html',
            'flag': 'admin/create/flag.html',
            'team': 'admin/create/team.html',
        }
        if len(args) == 1 and args[0] in self.game_objects.keys():
            self.render(self.game_objects[args[0]], errors=None)
        else:
            self.render("public/404.html")

    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        self.game_objects = {
            'corporation': self.create_corporation,
            'box': self.create_box,
            'flag': self.create_flag,
            'team': self.create_team,
        }
        if len(args) == 1 and args[0] in self.game_objects.keys():
            self.game_objects[args[0]]()
        else:
            self.render("public/404.html")

    def create_corporation(self):
        form = Form(name="Enter a name")
        if form.validate(self.request.arguments):
            corporation = Corporation(
                name=self.get_argument('name')
            )
            dbsession.add(corporation)
            dbsession.flush()
        else:
            self.render("admin/create/corporation.html", errors=form.errors)

    def create_box(self):
        form = Form(
            name="Enter a box name",
            ip_address="Enter an IP address",
            description="Enter a description",
            difficulty="Select a difficulty",
            avatar="Please upload an avatar",
        )
        if form.validate(self.request.arguments):
            box = Box(
                name=unicode(name),
                ip_address=unicode(ip_address),
                description=unicode(description),
                difficulty=unicode(difficulty),
                avatar=unicode(avatar_uuid),
            )
            dbsession.add(box)
            dbsession.flush()
            self.render("admin/view/box.html")
        else:
            self.render("admin/create/box.html", errors=form.errors)

    def create_flag(self):
        pass

    def create_team(self):
        form = Form(team="Enter a team name", motto="Enter a team motto")
        if form.validate(self.request.arguments):
            team = Team(
                name=unicode(self.request.arguments['team'][0]),
                motto=unicode(self.request.arguments['motto'][0]),
            )
            self.dbsession.add(team)
            self.dbsession.flush()
            self.render(
                "admin/view/team.html", errors=None)
        else:
            self.render("admin/create/team.html", errors=form.errors)


class AdminViewHandler(BaseHandler):
    ''' View game objects '''

    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        self.game_objects = {
            'corporation': self.view_corporations,
            'box': self.view_boxes,
            'flag': self.view_flags,
            'team': self.view_teams,
            'user': self.view_users,
        }
        if len(args) == 1 and args[0] in self.game_objects.keys():
            self.game_objects[args[0]]()
        else:
            self.render("public/404.html")

    def view_corporations(self):
        self.render("admin/view/corporation.html", errors=None)

    def view_boxes(self):
        self.render("admin/view/box.html", errors=None)

    def view_flags(self):
        self.render("admin/view/flag.html", errors=None)

    def view_teams(self):
        self.render("admin/view/team.html", errors=None)

    def view_users(self):
        self.render("admin/view/user.html", errors=None)


class AdminEditHandler(BaseHandler):
    ''' Edit game objects '''

    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        self.game_objects = {
            'corporation': self.edit_corporations,
            'box': self.edit_boxes,
            'flag': self.edit_flags,
            'team': self.edit_teams,
            'user': self.edit_users,
        }
        if len(args) == 1 and args[0] in self.game_objects.keys():
            self.game_objects[args[0]]()
        else:
            self.render("public/404.html")

    def edit_corporations(self):
        pass

    def edit_boxes(self):
        pass

    def edit_flags(self):
        pass

    def edit_teams(self):
        pass

    def edit_users(self):
        pass
