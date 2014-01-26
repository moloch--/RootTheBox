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

There's a lot of code in here ... and it's mostly ugly validation code...

This file contains all of the adminstrative functions.

'''


import re
import os
import imghdr
import defusedxml.minidom
import xml.etree.cElementTree as ET

from uuid import uuid4
from tempfile import NamedTemporaryFile
from string import ascii_letters, digits, printable
from base64 import b64encode
from hashlib import md5
from libs.Form import Form
from libs.LoggingHelpers import ObservableLoggingHandler
from libs.EventManager import EventManager
from libs.SecurityDecorators import *
from models.Team import Team
from models.Box import Box
from models.Flag import Flag
from models.SourceCode import SourceCode
from models.MarketItem import MarketItem
from models.Corporation import Corporation
from models.RegistrationToken import RegistrationToken
from models.GameLevel import GameLevel
from models.IpAddress import IpAddress
from models.Swat import Swat
from models.Hint import Hint
from handlers.BaseHandlers import BaseHandler, BaseWebSocketHandler
from models.User import ADMIN_PERMISSION
from models.Flag import FLAG_STATIC, FLAG_REGEX, FLAG_FILE
from setup.importers import import_xml


class AdminCreateHandler(BaseHandler):
    ''' Handler used to create game objects '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Renders Corp/Box/Flag create pages '''
        self.game_objects = {
            'corporation': 'admin/create/corporation.html',
                    'box': 'admin/create/box.html',
                   'flag': 'admin/create/flag.html',
             'flag/regex': 'admin/create/flag-regex.html',
              'flag/file': 'admin/create/flag-file.html',
            'flag/static': 'admin/create/flag-static.html',
                   'team': 'admin/create/team.html',
             'game_level': 'admin/create/game_level.html',
                   'hint': 'admin/create/hint.html',
        }
        if len(args) == 1 and args[0] in self.game_objects:
            self.render(self.game_objects[args[0]], errors=None)
        else:
            self.render("public/404.html")

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Calls a function based on URL '''
        self.game_objects = {
            'corporation': self.create_corporation,
                    'box': self.create_box,
              'flag/file': self.create_flag_file,
             'flag/regex': self.create_flag_regex,
            'flag/static': self.create_flag_static,
                   'team': self.create_team,
             'game_level': self.create_game_level,
                   'hint': self.create_hint,
        }
        if len(args) == 1 and args[0] in self.game_objects:
            self.game_objects[args[0]]()
        else:
            self.render("public/404.html")

    def create_corporation(self):
        ''' Add a new corporation to the database '''
        try:
            corp_name = self.get_argument('corporation_name', '')
            if Corporation.by_name(corp_name) is not None:
                raise ValueError("Corporation name already exists")
            else:
                corporation = Corporation()
                corporation.name = corp_name
                self.dbsession.add(corporation)
                self.dbsession.commit()
                self.redirect('/admin/view/game_objects')
        except ValueError as error:
            self.render("admin/create/corporation.html", errors=["%s" % error])

    def create_box(self):
        ''' Create a box object '''
        try:
            lvl = self.get_argument('game_level', '')
            game_level = abs(int(lvl)) if lvl.isdigit() else 0
            corp_uuid = self.get_argument('corporation_uuid', '')
            if Box.by_name(self.get_argument('name', '')) is not None:
                self.render("admin/create/box.html",
                    errors=["Box name already exists"]
                )
            elif Corporation.by_uuid(corp_uuid) is None:
                self.render("admin/create/box.html", errors=["Corporation does not exist"])
            elif GameLevel.by_number(game_level) is None:
                self.render("admin/create/box.html", errors=["Game level does not exist"])
            else:
                box = self._make_box(game_level)
                self.dbsession.commit()
                self.redirect('/admin/view/game_objects')
        except ValueError as error:
            self.render('admin/create/box.html', errors=["%s" % error])

    def create_flag_static(self):
        ''' Create a flag '''
        try:
            self._mkflag(FLAG_STATIC)
        except Exception as error:
            self.render('admin/create/flag-static.html', errors=[str(error)])

    def create_flag_regex(self):
        ''' Create a flag '''
        try:
            self._mkflag(FLAG_REGEX)
        except Exception as error:
            self.render('admin/create/flag-regex.html', errors=[str(error)])

    def create_flag_file(self):
        ''' Create a flag '''
        try:
            self._mkflag(FLAG_FILE, is_file=True)
        except Exception as error:
            self.render('admin/create/flag-file.html', errors=[str(error)])

    def create_team(self):
        ''' Create a new team in the database '''
        team = Team()
        team.name = self.get_argument('team_name', '')
        team.motto = self.get_argument('motto', '')
        level_0 = GameLevel.all()[0]
        team.game_levels.append(level_0)
        self.dbsession.add(team)
        self.dbsession.commit()
        self.redirect('/admin/view/user_objects')

    def create_game_level(self):
        ''' Creates a game level '''
        try:
            lvl = self.get_argument('level_number', '')
            game_level = abs(int(lvl)) if lvl.isdigit() else 0
            if GameLevel.by_number(game_level) is not None:
                self.render('admin/create/game_level.html',
                    errors=["Game level number must be unique"]
                )
            else:
                self._make_level(game_level)
                self.redirect('/admin/view/game_levels')
        except ValueError:
            self.render('admin/create/game_level.html',
                errors=["Invalid level number"]
            )

    def create_hint(self):
        ''' Add hint to database '''
        box = Box.by_uuid(self.get_argument('box_uuid', ''))
        if box is not None:
            try:
                hint = Hint(box_id=box.id)
                hint.price = self.get_argument('price', '')
                hint.description = self.get_argument('description', '')
                self.dbsession.add(hint)
                self.dbsession.commit()
                self.redirect('/admin/view/game_objects')
            except ValueError as error:
                self.render('admin/create/hint.html', errors=["%s" % error])
        else:
            self.render('admin/create/hint.html', errors=["Box does not exist"])

    def _mkflag(self, flag_type, is_file=False):
        name = self.get_argument('flag_name', '')
        if is_file:
            if not 'flag' in self.request.files:
                raise ValueError('No file in request')
            token = self.request.files['flag'][0]['body']
        else:
            token = self.get_argument('token', '')
        description = self.get_argument('description', '')
        reward = int(self.get_argument('reward', ''))
        box = Box.by_uuid(self.get_argument('box_uuid', ''))
        if box is None:
            raise ValueError('Box does not exist')
        flag = Flag.create_flag(flag_type, box, name, token, description, reward)
        self.dbsession.add(flag)
        self.dbsession.commit()
        self.redirect('/admin/view/game_objects')

    def _make_box(self, level_number):
        ''' Creates a box in the database '''
        corp = Corporation.by_uuid(self.get_argument('corporation_uuid'))
        level = GameLevel.by_number(level_number)
        box = Box(corporation_id=corp.id, game_level_id=level.id)
        box.name = self.get_argument('name', '')
        box.description = self.get_argument('description', '')
        box.difficulty = self.get_argument('difficulty', '')
        self.dbsession.add(box)
        self.dbsession.commit()
        if 'avatar' in self.request.files:
            box.avatar = self.request.files['avatar'][0]['body']
        return box

    def _make_level(self, level_number):
        '''
        Creates a new level in the database, the levels are basically a
        linked-list where each level points to the next, and the last points to
        None.  This function creates a new level and sorts everything based on
        the 'number' attrib
        '''
        new_level = GameLevel()
        new_level.number = level_number
        new_level.buyout = self.get_argument('buyout', '')
        game_levels = GameLevel.all()
        game_levels.append(new_level)
        game_levels = sorted(game_levels)
        index = 0
        for level in game_levels[:-1]:
            level.next_level_id = game_levels[index + 1].id
            self.dbsession.add(level)
            index += 1
        game_levels[0].number = 0
        self.dbsession.add(game_levels[0])
        game_levels[-1].next_level_id = None
        self.dbsession.add(game_levels[-1])
        self.dbsession.commit()


class AdminViewHandler(BaseHandler):
    ''' View game objects '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Calls a view function based on URI '''
        uri = {
              'game_objects': self.view_game_objects,
               'game_levels': self.view_game_levels,
              'user_objects': self.view_user_objects,
            'market_objects': self.view_market_objects,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def view_market_objects(self):
        self.render('admin/view/market_objects.html', errors=None)

    def view_game_objects(self):
        ''' Renders the view corporations page '''
        self.render("admin/view/game_objects.html", errors=None)

    def view_game_levels(self):
        self.render("admin/view/game_levels.html", errors=None)

    def view_user_objects(self):
        ''' Renders the view registration token page '''
        self.render('admin/view/user_objects.html', errors=None)


class AdminAjaxObjectDataHandler(BaseHandler):
    ''' Handles AJAX data for admin handlers '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        game_objects = {
            'game_level': GameLevel,
            'corporation': Corporation,
            'flag': Flag,
            'user': User,
            'team': Team,
             'box': Box,
            'hint': Hint,
        }
        obj_name = self.get_argument('obj', '')
        uuid = self.get_argument('uuid', '')
        if obj_name in game_objects.keys():
            obj = game_objects[obj_name].by_uuid(uuid)
            if obj is not None:
                self.write(obj.to_dict())
            else:
                self.write({'Error': 'Invalid uuid.'})
        else:
            self.write({'Error': 'Invalid object type.'})
        self.finish()


class AdminEditHandler(BaseHandler):
    ''' Edit game objects '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Just redirect to the corisponding /view page '''
        uri = {
            'corporation': 'game_objects',
                    'box': 'game_objects',
                   'flag': 'game_objects',
                   'team': 'game_objects',
                   'user': 'user_objects',
                   'ipv4': 'game_objects',
                   'ipv6': 'game_objects',
             'game_level': 'game_levels',
              'box_level': 'game_levels',
                   'hint': 'game_objects',
            'market_item': 'market_objects',
        }
        if len(args) == 1 and args[0] in uri:
            self.redirect('/admin/view/%s' % uri[args[0]])
        else:
            self.render("public/404.html")

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Calls an edit function based on URL '''
        uri = {
            'corporation': self.edit_corporations,
                    'box': self.edit_boxes,
                   'flag': self.edit_flags,
                   'team': self.edit_teams,
                   'user': self.edit_users,
                   'ipv4': self.edit_ipv4,
                   'ipv6': self.edit_ipv6,
             'game_level': self.edit_game_level,
              'box_level': self.box_level,
                   'hint': self.edit_hint,
            'market_item': self.edit_market_item,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def edit_corporations(self):
        ''' Updates corporation object in the database '''
        corp = Corporation.by_uuid(self.get_argument('uuid', ''))
        if corp is not None:
            try:
                name = self.get_argument('name', '')
                if name != corp.name:
                    logging.info("Updated corporation name %s -> %s" % (corp.name, name))
                    corp.name = name
                    self.dbsession.add(corp)
                    self.dbsession.commit()
                self.redirect('/admin/view/game_objects')
            except ValueError as error:
                self.render("admin/view/game_objects.html", errors=["%s" % error])
        else:
            self.render("admin/view/game_objects.html",
                errors=["Corporation does not exist"]
            )

    def edit_boxes(self):
        '''
        Edit existing boxes in the database, and log the changes
        '''
        box = Box.by_uuid(self.get_argument('uuid', ''))
        if box is not None:
            try:
                name = self.get_argument('name', '')
                if name != box.name:
                    if Box.by_name(name) is None:
                        logging.info("Updated box name %s -> %s" % (box.name, name,))
                        box.name = name
                    else:
                        raise ValueError("Box name already exists")
                corp = Corporation.by_uuid(self.get_argument('corporation_uuid'))
                if corp is not None and corp.id != box.corporation_id:
                    logging.info("Updated %s's corporation %s -> %s" %
                        (box.name, box.corporation_id, corp.id,))
                    box.corporation_id = corp.id
                elif corp is None:
                    raise ValueError("Corporation does not exist")
                description = self.get_argument('description', '')
                if description != box._description:
                    logging.info("Updated %s's description %s -> %s" %
                        (box.name, box.description, description,)
                    )
                    box.description = description
                difficulty = self.get_argument('difficulty', '')
                if difficulty != box.difficulty:
                    logging.info("Updated %s's difficulty %s -> %s" %
                        (box.name, box.difficulty, difficulty,)
                    )
                    box.difficulty = difficulty
                if 'avatar' in self.request.files:
                    box.avatar = self.request.files['avatar'][0]['body']
                self.dbsession.add(box)
                self.dbsession.commit()
                self.redirect("/admin/view/game_objects")
            except ValueError as error:
                self.render("admin/view/game_objects.html", errors=["%s" % error])
        else:
            self.render("admin/view/game_objects.html",
                errors=["Box does not exist"]
            )

    def edit_flags(self):
        ''' Super ugly code, yes - Edit existing flags in the database '''
        flag = Flag.by_uuid(self.get_argument('uuid', ''))
        if flag is not None:
            try:
                name = self.get_argument('name', '')
                if flag.name != name:
                    if Flag.by_name(name) is None:
                        logging.info("Updated flag name %s -> %s" %
                            (flag.name, name,)
                        )
                        flag.name = name
                    else:
                        raise ValueError("Flag name already exists")
                token = self.get_argument('token', '')
                if flag.token != token:
                    if Flag.by_token(token) is None:
                        logging.info("Updated %s's token %s -> %s" %
                            (flag.name, flag.token, token)
                        )
                        flag.token = token
                    else:
                        raise ValueError("Token is not unique")
                description = self.get_argument('description', '')
                if flag._description != description:
                    logging.info("Updated %s's description %s -> %s" %
                        (flag.name, flag._description, description,)
                    )
                    flag.description = description
                logging.info("Updated %s's value %d -> %d" %
                    (flag.name, flag.value, reward_value,)
                )
                flag.value = self.get_argument('value', '')
                box = Box.by_uuid(self.get_argument('box_uuid', ''))
                if box is not None and flag not in box.flags:
                    logging.info("Updated %s's box %d -> %d" %
                        (flag.name, flag.box_id, box.id)
                    )
                    flag.box_id = box.id
                elif box is None:
                    raise ValueError("Box does not exist")
                self.dbsession.add(flag)
                self.dbsession.commit()
                self.redirect("admin/view/game_objects")
            except ValueError as error:
                self.render("admin/view/game_objects.html", errors=["%s" % error])
        else:
            self.render("admin/view/game_objects.html",
                errors=["Flag does not exist"]
            )

    def edit_teams(self):
        ''' Edit existing team objects in the database '''
        team = Team.by_uuid(self.get_argument('uuid', ''))
        if team is not None:
            try:
                name = self.get_argument('name', '')
                if team.name != name:
                    logging.info("Updated team name %s -> %s" % (team.name, name))
                    team.name = name
                motto = self.get_argument('motto', '')
                if team.motto != motto:
                    logging.info("Updated %s's motto %s -> %s" % (team.name, team.motto, motto))
                    team.motto = motto
                self.dbsession.add(team)
                self.dbsession.close()
                self.redirect("/admin/view/user_objects")
            except ValueError as error:
                self.render("admin/view/user_objects.html", errors=["%s" % error])
        else:
            self.render("admin/view/user_objects.html", errors=["Team does not exist"])

    def edit_users(self):
        ''' Update user objects in the database '''
        user = User.by_uuid(self.get_argument('uuid', ''))
        if user is not None:
            try:
                handle = self.get_argument('handle', '')
                if user.handle != handle:
                    if User.by_handle(handle) is None:
                        logging.info("Updated user handle %s -> %s" % (user.handle, handle))
                        user.handle = handle
                    else:
                        raise ValueError("Handle is already in use")
                hash_algorithm = self.get_argument('hash_algorithm', '')
                if hash_algorithm in user.algorithms and user.algorithm != hash_algorithm:
                    if 0 < len(self.get_argument('bank_password', '')):
                        logging.info("Updated %s's hashing algorithm %s -> %s" %
                            (user.handle, user.algorithm, hash_algorithm,)
                        )
                        user.algorithm = hash_algorithm
                    else:
                        raise ValueError("You must provide a new bank password when updating the hashing algorithm")
                else:
                    raise ValueError("Not a valid hash algorithm")
                password = self.get_argument('password', '')
                if 0 < len(password):
                    user.password = password
                bank_password = self.get_argument('bank_password', '')
                if 0 < len(bank_password):
                    user.bank_password = bank_password
                team = Team.by_uuid(self.get_argument('team_uuid'))
                if team is not None and user not in team.members:
                    logging.info("Updated %s's team %s -> %s" %
                        (user.handle, user.team_id, team.name))
                    user.team_id = team.id
                else:
                    raise ValueError("Team does not exist in database")
                self.dbsession.add(user)
                self.dbsession.commit()
            except ValueError as error:
                self.render("admin/view/user_objects.html", errors=["%s" % error])
        else:
            self.render("admin/view/user_objects.html", errors=["User does not exist"])

    def edit_ipv4(self):
        ''' Add ipv4 addresses to a box (sorta edits the box object) '''
        errors = []
        box = Box.by_uuid(self.get_argument('box_uuid'))
        if box is not None:
            ips_string = self.get_argument('ipv4').replace('\n', ',')
            ips = filter(lambda char: char in "1234567890.,", ips_string).split(",")
            for ip in filter(lambda ip: 0 < len(ip), ips):
                try:
                    if Box.by_ip_address(ip) is None:
                        addr = IpAddress(box_id=box.id, v4=ip)
                        dbsession.add(addr)
                    else:
                        errors.append("%s has already been assigned to %s." %
                            (ip, box.name,)
                        )
                except ValueError:
                    errors.append(
                        "'%s' is not a valid IPv4 address" % str(ip[:15])
                    )
            dbsession.flush()
        else:
            errors.append("Box does not exist")
        self.render("admin/view/game_objects.html", errors=errors)

    def edit_ipv6(self):
        ''' Add ipv6 addresses to a box (sorta edits the box object) '''
        errors = []
        box = Box.by_uuid(self.get_argument('box_uuid'))
        if box is not None:
            ips_string = self.get_argument('ipv6').replace('\n', ',').lower()
            ips = filter(lambda char: char in "1234567890abcdef:,", ips_string).split(",")
            for ip in filter(lambda ip: 0 < len(ip), ips):
                try:
                    box = Box.by_ip_address(ip)
                    if box is None:
                        addr = IpAddress(box_id=box.id, v6=ip)
                        dbsession.add(addr)
                    else:
                        errors.append(
                            "%s has already been assigned to %s." % (ip, box.name,)
                        )
                except ValueError:
                    errors.append(
                        "'%s' is not a valid IPv6 address" % str(ip[:39])
                    )
            dbsession.flush()
        else:
            errors.append("Box does not exist")
        self.render("admin/view/game_objects.html", errors=errors)

    def edit_game_level(self):
        ''' Update game level objects '''
        errors = []
        level = GameLevel.by_uuid(self.get_argument('uuid'))
        try:
            new_number = int(self.get_argument('number', ''))
            new_buyout = int(self.get_argument('buyout', ''))
            if level.number != new_number and GameLevel.by_number(new_number) is None:
                level.number = new_number
                self.dbsession.add(level)
                # Fix the linked-list
                game_levels = sorted(GameLevel.all())
                index = 0
                for game_level in game_levels[:-1]:
                    game_level.next_level_id = game_levels[index + 1].id
                    self.dbsession.add(game_level)
                    index += 1
                game_levels[0].number = 0
                self.dbsession.add(game_levels[0])
                game_levels[-1].next_level_id = None
                self.dbsession.add(game_levels[-1])
            if GameLevel.by_number(new_number) is not None:
                errors.append("GameLevel number is not unique")
            if level.buyout != new_buyout:
                level.buyout = new_buyout
                self.dbsession.add(level)
            self.dbsession.commit()
        except ValueError:
            errors.append("That was not a number ...")
        self.render("admin/view/game_levels.html", errors=errors)

    def box_level(self):
        ''' Changes a boxs level '''
        errors = []
        box = Box.by_uuid(self.get_argument('box_uuid'))
        level = GameLevel.by_uuid(self.get_argument('level_uuid'))
        if box is not None and level is not None:
            box.game_level_id = level.id
            self.dbsession.add(box)
            self.dbsession.commit()
        elif box is None:
            errors.append("Box does not exist")
        elif level is None:
            errors.append("GameLevel does not exist")
        self.render("admin/view/game_levels.html", errors=errors)

    def edit_hint(self):
        ''' Edit a hint object '''
        hint = Hint.by_uuid(self.get_argument('uuid', ''))
        if hint is not None:
            try:
                logging.debug("Edit hint object with uuid of %s" % hint.uuid)
                price = self.get_argument('price', hint.price)
                if hint.price != price:
                    hint.price = price
                description = self.get_argument('description', hint.description)
                if hint.description != description:
                    hint.description = description
                self.dbsession.add(hint)
                self.dbsession.commit()
                self.redirect('/admin/view/game_objects')
            except ValueError as error:
                self.render("admin/view/game_objects.html", errors=["%s" % error])
        else:
            self.render("admin/view/game_objects.html", errors=["User does not exist"])


    def edit_market_item(self):
        ''' Change a market item's price '''
        item = MarketItem.by_uuid(self.get_argument('item_uuid', ''))
        if item is not None:
            try:
                price = self.get_argument('price', item.price)
                if item.price != price:
                    item.price = price
                self.dbsession.add(item)
                self.dbsession.flush()
                self.redirect('/admin/view/market_objects')
            except ValueError:
                self.render('admin/view/market_objects.html',
                    errors=["Invalid price."]
                )
        else:
            self.render('admin/view/market_objects.html',
                errors=["Item does not exist."]
            )


class AdminDeleteHandler(BaseHandler):
    ''' Delete flags/ips from the database '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Used to delete database objects '''
        uri = {
                     'ip': self.del_ip,
                   'flag': self.del_flag,
                   'hint': self.del_hint,
                    'box': self.del_box,
            'corporation': self.del_corp,
                   'user': self.del_user,
                   'team': self.del_team,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def del_ip(self):
        ''' Delete an ip address object '''
        ip = IpAddress.by_address(self.get_argument('ip', ''))
        if ip is not None:
            logging.info("Deleted IP address: '%s'" % str(ip))
            self.dbsession.delete(ip)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects")
        else:
            logging.info("IP address (%r) does not exist in database" %
                self.get_argument('ip', '')
            )
            self.render("admin/view/game_objects.html",
                errors=["IP does not exist in database"]
            )

    def del_flag(self):
        ''' Delete a flag object from the database '''
        flag = Flag.by_uuid(self.get_argument('uuid', ''))
        if flag is not None:
            logging.info("Deleted flag: %s " % flag.name)
            self.dbsession.delete(flag)
            self.dbsession.commit()
            self.redirect('/admin/view/game_objects')
        else:
            logging.info("Flag (%r) does not exist in the database" %
                self.get_argument('uuid', '')
            )
            self.render("admin/view/game_objects.html",
                errors=["Flag does not exist in database."]
            )

    def del_hint(self):
        ''' Delete a hint from the database '''
        hint = Hint.by_uuid(self.get_argument('uuid', ''))
        if hint is not None:
            logging.info("Delete hint: %s" % hint.uuid)
            self.dbsession.delete(hint)
            self.dbsession.commit()
            self.redirect('/admin/view/game_objects')
        else:
            self.render('admin/view/game_objects.html',
                errors=["Hint does not exist in database."]
            )

    def del_corp(self):
        ''' Delete a corporation '''
        corp = Corporation.by_uuid(self.get_argument('uuid', ''))
        if corp is not None:
            logging.info("Delete corporation: %s" % corp.name)
            self.dbsession.delete(corp)
            self.dbsession.commit()
            self.redirect('/admin/view/game_objects')
        else:
            self.render('admin/view/game_objects.html',
                errors=["Corporation does not exist in database."]
            )

    def del_box(self):
        ''' Delete  a box '''
        box = Box.by_uuid(self.get_argument('uuid', ''))
        if box is not None:
            logging.info("Delete box: %s" % box.name)
            self.dbsession.delete(box)
            self.dbsession.commit()
            self.redirect('/admin/view/game_objects')
        else:
            self.render('admin/view/game_objects.html',
                errors=["Box does not exist in database."]
            )

    def del_user(self):
        ''' Delete a user '''
        user = User.by_uuid(self.get_argument('uuid', ''))
        if user is not None:
            logging.info("Delete user: %s" % user.handle)
            self.dbsession.delete(user)
            self.dbsession.commit()
            self.redirect('/admin/view/user_objects')
        else:
            self.render('admin/view/user_objects.html',
                errors=["User does not exist in database."]
            )


class AdminLockHandler(BaseHandler):
    ''' Used to manually lock/unlocked accounts '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Toggle account lock '''
        user = User.by_uuid(self.get_argument('uuid', ''))
        if user is not None:
            user.locked = False if user.locked else True
            self.dbsession.add(user)
            self.dbsession.commit()
        self.redirect('/admin/view/user_objects')


class AdminRegTokenHandler(BaseHandler):
    ''' Manages registration tokens '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Call method based on URI '''
        uri = {
            'create': self.create,
              'view': self.view,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Used to delete regtokens '''
        token_value = self.get_argument('token_value', '')
        reg_token = RegistrationToken.by_value(token_value)
        if reg_token is not None:
            self.dbsession.delete(reg_token)
            self.dbsession.commit()
            self.redirect('/admin/regtoken/view')
        else:
            self.render('admin/view/token.html',
                errors=["Token does not exist"]
            )

    def create(self):
        ''' Adds a registration token to the db and displays the value '''
        token = RegistrationToken()
        self.dbsession.add(token)
        self.dbsession.commit()
        self.render('admin/create/token.html', token=token)

    def view(self):
        ''' View all reg tokens '''
        self.render('admin/view/token.html', errors=None)


class AdminSourceCodeMarketHandler(BaseHandler):
    ''' Add source code files to the source code market '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render('admin/upgrades/source_code_market.html', errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {
            '/add': self.add_source_code,
            '/delete': self.delete_source_code,
        }
        if 1 == len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def add_source_code(self):
        box = Box.by_uuid(self.get_argument('box_uuid'))
        if box is not None:
            if not 'source_archive' in self.request.files and 0 < len(self.request.files['source_archive']):
                self.render('admin/upgrades/source_code_market.html',
                    errors=["No file data"]
                )
            else:
                try:
                    price = abs(int(self.get_argument('price', 'NaN')))
                    self.create_source_code(box, price)
                    self.render('admin/upgrades/source_code_market.html',
                        errors=None
                    )
                except ValueError:
                    self.render('admin/upgrades/source_code_market.html',
                        errors=["Price must be an integer"]
                    )
        else:
            self.render('admin/upgrades/source_code_market.html',
                errors=["The selected box does not exist"]
            )

    def create_source_code(self, box, price):
        ''' Save file data and create object in database '''
        description = unicode(self.get_argument('description', ''))
        file_name = unicode(
            self.request.files['source_archive'][0]['filename']
        )
        source_code = SourceCode(
            file_name=file_name,
            box_id=box.id,
            price=price,
            description=description,
        )
        self.dbsession.add(source_code)
        self.dbsession.flush()
        file_data = self.request.files['source_archive'][0]['body']
        root = self.application.settings['source_code_market_dir']
        save_file = open(str(root + '/' + source_code.uuid), 'w')
        source_code.checksum = self.get_checksum(file_data)
        save_file.write(b64encode(file_data))
        save_file.close()
        self.dbsession.add(source_code)
        self.dbsession.commit()

    def get_checksum(self, data):
        ''' Calculate checksum of file data '''
        return md5(data).hexdigest()

    def delete_source_code(self):
        ''' Delete source code file '''
        uuid = self.get_argument('box_uuid', '')
        box = Box.by_uuid(uuid)
        if box is not None and box.source_code is not None:
            source_code_uuid = box.source_code.uuid
            self.dbsession.delete(box.source_code)
            self.dbsession.commit()
            root = self.application.settings['source_code_market_dir']
            source_code_path = root + '/' + source_code_uuid
            logging.info("Delete souce code market file: %s (box: %s)" %
                (source_code_path, box.name,)
            )
            if os.path.exists(source_code_path):
                os.unlink(source_code_path)
            errors = None
        else:
            errors = ["Box does not exist, or contains no source code"]
        self.render('admin/upgrades/source_code_market.html', errors=errors)


class AdminSwatHandler(BaseHandler):
    ''' Manage SWAT requests '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render_page()

    def render_page(self, errors=None):
        ''' Render page with extra arguments '''
        if errors is not None and not isinstance(errors, list):
            errors = [str(errors), ]
        self.render('admin/upgrades/swat.html',
            pending_bribes=Swat.all_pending(),
            in_progress_bribes=Swat.all_in_progress(),
            completed_bribes=Swat.all_completed(),
            errors=errors,
        )

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Accept/Complete bribes '''
        uri = {
            '/accept': self.accept_bribe,
            '/complete': self.complete_bribe,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def accept_bribe(self):
        ''' Accept bribe, and lock user's account '''
        swat = Swat.by_uuid(self.get_argument('uuid', ''))
        if swat is not None and not swat.completed:
            logging.info("Accepted SWAT with uuid: %s", swat.uuid)
            swat.accepted = True
            swat.target.locked = True
            self.dbsession.add(swat)
            self.dbsession.add(swat.target)
            self.dbsession.commit()
            self.render_page()
        else:
            logging.warn("Invalid request to accept bribe with uuid: %r" %
                (self.get_argument('uuid', ''),)
            )
            self.render_page('Requested SWAT object does not exist')

    def complete_bribe(self):
        ''' Complete bribe and unlock user's account '''
        swat = Swat.by_uuid(self.get_argument('uuid', ''))
        if swat is not None and not swat.completed:
            logging.info("Completed SWAT with uuid: %s", swat.uuid)
            swat.completed = True
            swat.target.locked = False
            self.dbsession.add(swat)
            self.dbsession.add(swat.target)
            self.dbsession.commit()
            self.render_page()
        else:
            logging.warn("Invalid request to complete bribe with uuid: %r" %
                (self.get_argument('uuid', ''),)
            )
            self.render_page('Requested SWAT object does not exist')


class AdminConfigurationHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render('admin/configuration.html',
            warning=None,
            errors=[],
            config=self.config
        )

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Update configuration '''
        all_errors = []
        all_errors += self.game_name()
        all_errors += self.bot_config()
        all_errors += self.history_config()
        all_errors += self.cost_config()
        self.password_config()
        self.debug_config()
        self.config.save()
        self.render('admin/configuration.html',
            warning="Some configuration changes may require application restart to take affect.",
            errors=all_errors,
            config=self.config
        )

    def is_numeric_within(self, string, min_value, max_value):
        ''' Check if string is a number within a range '''
        try:
            return min_value <= int(string) <= max_value
        except ValueError:
            return False

    def filter_string(self, data):
        char_white_list = ascii_letters + digits + " -_:;"
        return filter(lambda char: char in char_white_list, data)

    def game_name(self):
        ''' Update game name configuration '''
        errors = []
        game_name = self.get_argument('game_name', self.config.game_name)
        game_name = self.filter_string(game_name)
        if 0 < len(game_name):
            if game_name != self.config.game_name:
                self.config.game_name = game_name
        else:
            errors.append("Game name must be at least 1 character long.")
        return errors

    def bot_config(self):
        ''' Updates bot related configuration '''
        errors = []
        # Update reward
        reward = self.get_argument('bot_reward', self.config.bot_reward)
        new_reward = filter(lambda char: char in digits, reward)
        if self.is_numeric_within(new_reward, 1, 10000):
            if new_reward != self.config.bot_reward:
                self.config.bot_reward = int(new_reward)
        else:
            errors.append("Bot reward must be $1 - $10,0000")
        # Update interval
        old_interval = int(self.config.bot_reward_interval / 60000)
        interval = self.get_argument('bot_reward_interval', old_interval)
        new_interval = filter(lambda char: char in digits, interval)
        if self.is_numeric_within(new_interval, 1, 30):
            if new_interval != old_interval:
                self.config.bot_reward_interval = int(new_interval)
        else:
            errors.append("Bot reward interval must be 1 - 30 mins")
        return errors

    def history_config(self):
        ''' Update history configuration '''
        errors = []
        old_interval = int(self.config.history_snapshot_interval / 60000)
        interval = self.get_argument('history_snapshot_interval', self.config.history_snapshot_interval)
        new_interval = filter(lambda char: char in digits, interval)
        if self.is_numeric_within(new_interval, 1, 30):
            if new_interval != old_interval:
                self.config.history_snapshot_interval = int(new_interval)
        else:
            self.errors.append("History interval must be 1 - 30 mins")
        return errors

    def password_config(self):
        ''' Updates password configuration '''
        password_length = self.get_argument('max_password_length', self.config.max_password_length)
        new_length = filter(lambda char: char in digits, password_length)
        if new_length != self.config.max_password_length:
            self.config.max_password_length = abs(int(new_length))

    def cost_config(self):
        ''' Update cost configurations '''
        # Update password upgrade cost
        errors = []
        pw_cost = self.get_argument('password_upgrade_cost', self.config.password_upgrade_cost)
        pw_cost = filter(lambda char: char in digits, pw_cost)
        if self.is_numeric_within(pw_cost, 100, 100000):
            if pw_cost != self.config.password_upgrade_cost:
                self.config.password_upgrade_cost = int(pw_cost)
        else:
            errors.append("Password upgrade cost must be $100 - $100,000")
        # Update bribe cost
        bribe_cost = self.get_argument('bribe_cost', self.config.bribe_cost)
        bribe_cost = filter(lambda char: char in digits, bribe_cost)
        if self.is_numeric_within(bribe_cost, 100, 100000):
            if bribe_cost != self.config.bribe_cost:
                self.config.bribe_cost = int(bribe_cost)
        else:
            errors.append("Bribe cost must be $100 - $100,000")
        return errors

    def debug_config(self):
        ''' Update debug configuration '''
        debug = self.get_argument('debug', str(self.config.debug).lower())
        if debug != str(self.config.debug).lower():
            self.config.debug = bool(debug == 'true')


class AdminGarbageCfgHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Download a Box's garbage file '''
        box = Box.by_uuid(self.get_argument('uuid', ''))
        if box is not None:
            data = box.get_garbage_cfg()
            self.set_header('Content-Type', 'text/plain')
            self.set_header(
                "Content-disposition", "attachment; filename=%s.garbage" % (
                    filter(lambda char: char in printable[:-38], box.name),
            ))
            self.set_header('Content-Length', len(data))
            self.write(data)


class AdminExportHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Export to document formats '''
        uri = {
            'xml': self.export_xml,
            'json': self.export_json,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def export_xml(self):
        ''' Create and write XML document to page '''
        xml_doc = self.create_xml()
        self.set_header('Content-Type', 'text/xml')
        self.set_header(
            "Content-disposition", "attachment; filename=%s.xml" % (
                filter(lambda char: char in printable[:-38], self.config.game_name),
        ))
        self.set_header('Content-Length', len(xml_doc))
        self.write(xml_doc.encode('utf-8'))
        self.finish()

    def create_xml(self):
        '''
        Exports the game objects to an XML doc.
        For the record, I hate XML with a passion.
        '''
        root = ET.Element("rootthebox")
        levels_elem = ET.SubElement(root, "gamelevels")
        levels_elem.set("count", str(GameLevel.count()))
        for level in GameLevel.all()[1:]:
            level.to_xml(levels_elem)
        corps_elem = ET.SubElement(root, "corporations")
        corps_elem.set("count", str(Corporation.count()))
        for corp in Corporation.all():
            corp.to_xml(corps_elem)
        xml_dom = defusedxml.minidom.parseString(ET.tostring(root))
        return xml_dom.toprettyxml()

    def export_json(self):
        pass


class AdminImportXmlHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Import setup files '''
        self.render('admin/import.html', success=None, errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        '''
        Import XML file uploaded by the admin.
        '''
        if 'xml_file' in self.request.files:
            fxml = self._get_tmp()
            errors = []
            success = None
            if import_xml(fxml):
                success = "Successfully imported XML objects"
            else:
                errors.append("Failed to parse file correctly.")
            os.unlink(fxml)
            self.render('admin/import.html',
                success=success,
                errors=errors
            )
        else:
            self.render('admin/import.html',
                success=None,
                errors=["No file data."],
            )

    def _get_tmp(self):
        ''' Creates a tmp file with the file data '''
        data = self.request.files['xml_file'][0]['body']
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.write(data)
        tmp_file.close()
        return tmp_file.name


class AdminLogViewerHandler(BaseHandler):

    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Import setup files '''
        if self.config.enable_logviewer:
            requested_level = self.get_argument('loglevel', 'DEBUG')
            if requested_level in self.log_levels:
                level = requested_level
            else:
                level = 'DEBUG'
            self.render('admin/logviewer.html', log_level=level)
        else:
            self.render('public/404.html')


class AdminLogViewerSocketHandler(BaseWebSocketHandler):

    @restrict_ip_address
    @restrict_origin
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def open(self):
        ''' Add this object as an observer '''
        self.observerable_log = None
        if self.config.enable_logviewer:
            self.observerable_log = ObservableLoggingHandler.instance()
            self.observerable_log.add_observer(self)
        else:
            self.close()

    def update(self, messages):
        ''' Write logging messages to wsocket '''
        self.write_message({'messages': messages})

    def on_close(self):
        ''' Remove the ref to this object '''
        if self.observerable_log is not None:
            self.observerable_log.remove_observer(self)
