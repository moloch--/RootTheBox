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


from libs.Form import Form
from libs.SecurityDecorators import *
from models import dbsession, Team, Box, Flag, \
    Corporation, RegistrationToken
from handlers.BaseHandlers import BaseHandler


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
            'game_level': 'admin/create/game_level.html'
        }
        if len(args) == 1 and args[0] in self.game_objects.keys():
            self.render(self.game_objects[args[0]], errors=None)
        else:
            self.render("public/404.html")

    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Calls a function based on URL '''
        self.game_objects = {
            'corporation': self.create_corporation,
            'box': self.create_box,
            'flag': self.create_flag,
            'team': self.create_team,
            'game_level': self.create_game_level,
        }
        if len(args) == 1 and args[0] in self.game_objects.keys():
            self.game_objects[args[0]]()
        else:
            self.render("public/404.html")

    def create_corporation(self):
        ''' Add a new corporation to the database '''
        form = Form(
            corporation_name="Enter a corporation name",
            description="Please enter a description",
        )
        if form.validate(self.request.arguments):
            if Corporation.by_name(self.get_argument('corporation_name')) is not None:
                self.render("admin/create/corporation.html", errors=["Name already exists"])
            else:
                corporation = Corporation(
                    name=unicode(self.get_argument('corporation_name')),
                    description=unicode(self.get_argument('description'))
                )
                dbsession.add(corporation)
                dbsession.flush()
                self.redirect('/admin/view/game_objects')
        else:
            self.render("admin/create/corporation.html", errors=form.errors)

    def create_box(self):
        ''' Create a box object '''
        form = Form(
            name="Enter a box name",
            ip_address="Enter an IP address",
            description="Enter a description",
            difficulty="Select a difficulty",
            avatar="Please upload an avatar",
        )
        if form.validate(self.request.arguments):
            box = Box(
                name=unicode(self.get_argument('name')),
                ip_address=unicode(self.get_argument('ip_address')),
                description=unicode(self.get_argument('description')),
                difficulty=unicode(self.get_argument('difficulty')),
            )
            dbsession.add(box)
            dbsession.flush()
            self.redirect('/admin/view/game_objects')
        else:
            self.render("admin/create/box.html", errors=form.errors)

    def create_flag(self):
        ''' Create a flag '''
        form = Form(
            box_uuid="Please select a box",
            name="Please enter a name",
            token="Please enter a token value",
        )
        if form.validate(self.request.arguments):
            flag = Flag(
                name=unicode(self.get_argument('name')),
                token=unicode(self.get_argument('token'))
            )
            dbsession.add(flag)
            dbsession.flush()
            self.redirect('/admin/view/game_objects')
        else:
            self.render("admin/create/flag.html", errors=form.errors)

    def create_team(self):
        ''' Create a new team in the database '''
        form = Form(team="Enter a team name", motto="Enter a team motto")
        if form.validate(self.request.arguments):
            team = Team(
                name=unicode(self.get_argument('team')),
                motto=unicode(self.get_argument('motto')),
            )
            dbsession.add(team)
            dbsession.flush()
            self.redirect('/admin/view/team')
        else:
            self.render("admin/create/team.html", errors=form.errors)

    def create_game_level(self):
        ''' '''
        form = Form(
            number="Please enter a level number",
            buyout="Please enter a buyout value",
        )
        if form.validate(self.request.arguments):
            if 0 < self.get_argument('number'):
                self.render('admin/create/game_level.html', errors=["Number must be greater than 0"])
            elif GameLevel.by_number(self.get_argument('number')) is not None:
                self.render('admin/create/game_level.html', errors=["Game level number must be unique"])
            else:
                new_level = GameLevel(
                    number=self.get_argument('number'),
                    buyout=self.get_argument('buyout'),
                )
                self.__mklevel__(new_level)
        else:
            self.render('admin/create/game_level.html', errors=form.errors)

    def __mklevel__(self, new_level):
        ''' Creates a new level in the database, and keeps everything sorted '''
        game_levels = GameLevel.all()
        game_levels.append(new_level)
        game_levels = sorted(game_levels)
        index = 0
        for level in game_levels[:-1]:
            level.next_level_id = game_levels[index + 1].id
            dbsession.add(level)
            index += 1
        game_levels[-1].next_level_id = None
        dbsession.add(game_levels[-1])
        dbsession.flush()


class AdminViewHandler(BaseHandler):
    ''' View game objects '''

    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        ''' Calls a view function based on URI '''
        uri = {
            'game_objects': self.view_game_objects,
            'game_levels': self.view_game_levels,
            'user': self.view_user_objects,
        }
        if len(args) == 1 and args[0] in uri.keys():
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def view_game_objects(self):
        ''' Renders the view corporations page '''
        self.render("admin/view/game_objects.html", errors=None)

    def view_game_levels(self):
        self.render("admin/view/game_levels.html", errors=None)

    def view_user_objects(self):
        ''' Renders the view registration token page '''
        self.render('admin/view/user_objects.html', errors=None)


class AdminAjaxObjectDataHandler(BaseHandler):

    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        game_objects = {
            'corporation': Corporation,
            'box': Box,
            'flag': Flag,
        }
        obj_name = self.get_argument('game_object', '')
        uuid = self.get_argument('uuid', '')
        if obj_name in game_objects.keys():
            obj = game_objects[obj].by_uuid(uuid)
            if obj is not None:
                self.write(obj.to_dict())
            else:
                self.write({'Error':'Invalid uuid.'})
        else:
            self.write({'Error':'Invalid object type.'})
        self.finish()


class AdminEditHandler(BaseHandler):
    ''' Edit game objects '''

    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Calls an edit function based on URL '''
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


class AdminRegTokenHandler(BaseHandler):
    ''' Manages registration tokens '''

    @authorized('admin')
    @restrict_ip_address
    def get(self, *args, **kwargs):
        uri = {
            'create': self.create,
            'view': self.view,
        }
        if len(args) == 1 and args[0] in uri.keys():
            uri[args[0]]()
        else:
            self.render("public/404.html")

    @authorized('admin')
    @restrict_ip_address
    def post(self, *args, **kwargs):
        ''' Used to delete regtokens '''
        token_value = self.get_argument('token_value', '__NULL__')
        reg_token = RegistrationToken.by_value(token_value)
        if reg_token is not None:
            dbsession.delete(reg_token)
            dbsession.flush()
            self.redirect('/admin/regtoken/view')
        else:
            logging.info("Token with value '%s' does not exist." % str(token_value))
            self.render('admin/view/token.html', errors=["Token does not exist"])

    def create(self):
        ''' Adds a registration token to the db and displays the value '''
        token = RegistrationToken()
        dbsession.add(token)
        dbsession.flush()
        self.render('admin/create/token.html', token=token)
    
    def view(self):
        ''' View all reg tokens '''
        self.render('admin/view/token.html', errors=None)