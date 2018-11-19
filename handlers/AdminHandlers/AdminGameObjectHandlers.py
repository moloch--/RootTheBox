# -*- coding: utf-8 -*-
'''
Created on Nov 24, 2014

@author: moloch

    Copyright 2014 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


CRUD for game objects:
    - Corporations
    - Boxes (and IpAddress)
    - Flags (and FlagAttachment)
    - Game Levels
    - Hints

'''

import logging
import re
import json

from handlers.BaseHandlers import BaseHandler
from models.Box import Box, FlagsSubmissionType
from models.Corporation import Corporation
from models.Category import Category
from models.GameLevel import GameLevel
from models.FlagAttachment import FlagAttachment
from models.FlagChoice import FlagChoice
from models.MarketItem import MarketItem
from models.Hint import Hint
from models.Team import Team
from models.Penalty import Penalty
from models.IpAddress import IpAddress
from models.User import ADMIN_PERMISSION
from models.Flag import Flag, FLAG_FILE, FLAG_REGEX, FLAG_STATIC, FLAG_DATETIME, FLAG_CHOICE
from libs.ValidationError import ValidationError
from libs.SecurityDecorators import *


class AdminCreateHandler(BaseHandler):

    ''' Handler used to create game objects '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Renders Corp/Box/Flag create pages '''
        game_objects = {
            'corporation': 'admin/create/corporation.html',
            'box': 'admin/create/box.html',
            'flag': 'admin/create/flag.html',
            'flag/regex': 'admin/create/flag-regex.html',
            'flag/file': 'admin/create/flag-file.html',
            'flag/static': 'admin/create/flag-static.html',
            'flag/datetime': 'admin/create/flag-datetime.html',
            'flag/choice': 'admin/create/flag-choice.html',
            'game_level': 'admin/create/game_level.html',
            'hint': 'admin/create/hint.html',
            'team': 'admin/create/team.html',
            'category': 'admin/create/category.html',
        }
        if len(args) and args[0] in game_objects:
            if args[0] == "hint":
                box = Box.by_uuid(self.get_argument("box", ""))
                self.render(game_objects[args[0]], box=box, errors=None)
            else:
                self.render(game_objects[args[0]], errors=None)
        else:
            self.render("public/404.html")

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Calls a function based on URL '''
        game_objects = {
            'corporation': self.create_corporation,
            'box': self.create_box,
            'flag/file': self.create_flag_file,
            'flag/regex': self.create_flag_regex,
            'flag/static': self.create_flag_static,
            'flag/datetime': self.create_flag_datetime,
            'flag/choice': self.create_flag_choice,
            'game_level': self.create_game_level,
            'hint': self.create_hint,
            'team': self.create_team,
            'category': self.create_category,
        }
        if len(args) and args[0] in game_objects:
            game_objects[args[0]]()
        else:
            self.render("public/404.html")

    def create_team(self):
        ''' Admins can create teams manually '''
        try:
            name = self.get_argument('team_name', '')
            if Team.by_name(name) is not None:
                raise ValidationError("Team already exists")
            team = Team()
            team.name = self.get_argument('team_name', '')
            team.motto = self.get_argument('motto', '')
            if not self.config.banking:
                team.money = 0
            level_0 = GameLevel.by_number(0)
            if not level_0:
                level_0 = GameLevel.all()[0]
            team.game_levels.append(level_0)
            self.dbsession.add(team)
            self.dbsession.commit()

            # Avatar
            avatar_select = self.get_argument('team_avatar_select', '')
            if avatar_select and len(avatar_select) > 0:
                team._avatar = avatar_select
            elif hasattr(self.request, 'files') and 'avatar' in self.request.files:
                team.avatar = self.request.files['avatar'][0]['body']
            self.dbsession.add(team)
            self.dbsession.commit()
            self.redirect('/admin/users')
        except ValidationError as error:
            self.render("admin/create/team.html", errors=[str(error), ])

    def create_corporation(self):
        ''' Add a new corporation to the database '''
        try:
            corp_name = self.get_argument('corporation_name', '')
            if Corporation.by_name(corp_name) is not None:
                raise ValidationError("Corporation name already exists")
            else:
                corporation = Corporation()
                corporation.name = corp_name
                self.dbsession.add(corporation)
                self.dbsession.commit()
                self.redirect('/admin/view/game_objects')
        except ValidationError as error:
            self.render("admin/create/corporation.html", errors=[str(error), ])

    def create_category(self):
        ''' Add a new category to the database '''
        try:
            category = self.get_argument('category', '')
            if Category.by_category(category) is not None:
                raise ValidationError("Category already exists")
            else:
                new_category = Category()
                new_category.category = category
                self.dbsession.add(new_category)
                self.dbsession.commit()
                self.redirect('/admin/view/categories')
        except ValidationError as error:
            self.render("admin/create/category.html", errors=[str(error), ])

    def create_box(self):
        ''' Create a box object '''
        try:
            game_level = self.get_argument('game_level', '')
            corp_uuid = self.get_argument('corporation_uuid', '')
            if Box.by_name(self.get_argument('name', '')) is not None:
                raise ValidationError("Box name already exists")
            elif Corporation.by_uuid(corp_uuid) is None:
                raise ValidationError("Corporation does not exist")
            elif GameLevel.by_number(game_level) is None:
                raise ValidationError("Game level does not exist")
            else:
                corp = Corporation.by_uuid(corp_uuid)
                level = GameLevel.by_number(game_level)
                box = Box(corporation_id=corp.id, game_level_id=level.id)
                box.name = self.get_argument('name', '')
                box.description = self.get_argument('description', '')
                box.flag_submission_type = FlagsSubmissionType[self.get_argument('flag_submission_type','')]
                box.difficulty = self.get_argument('difficulty', '')
                box.operating_system = self.get_argument('operating_system', '?')
                cat = Category.by_uuid(self.get_argument('category_uuid', ''))
                if cat is not None:
                    box.category_id = cat.id
                else:
                    box.category_id = None
                # Avatar
                avatar_select = self.get_argument('box_avatar_select', '')
                if avatar_select and len(avatar_select) > 0:
                    box._avatar = avatar_select
                elif hasattr(self.request, 'files') and 'avatar' in self.request.files:
                    box.avatar = self.request.files['avatar'][0]['body']
                self.dbsession.add(box)
                self.dbsession.commit()
                self.redirect("/admin/view/game_objects#%s" % box.uuid)
        except ValidationError as error:
            self.render('admin/create/box.html', errors=[str(error), ])

    def create_flag_static(self):
        ''' Create a static flag '''
        try:
            self._mkflag(FLAG_STATIC)
        except ValidationError as error:
            self.render('admin/create/flag-static.html', errors=[str(error)])

    def create_flag_regex(self):
        ''' Create a regex flag '''
        try:
            self._mkflag(FLAG_REGEX)
        except ValidationError as error:
            self.render('admin/create/flag-regex.html', errors=[str(error)])

    def create_flag_file(self):
        ''' Create a flag flag '''
        try:
            self._mkflag(FLAG_FILE, is_file=True)
        except ValidationError as error:
            self.render('admin/create/flag-file.html', errors=[str(error)])

    def create_flag_choice(self):
        ''' Create a multiple choice flag '''
        try:
            self._mkflag(FLAG_CHOICE)
        except ValidationError as error:
            self.render('admin/create/flag-choice.html', errors=[str(error)])

    def create_flag_datetime(self):
        ''' Create a datetime flag '''
        try:
            self._mkflag(FLAG_DATETIME)
        except ValidationError as error:
            self.render('admin/create/flag-datetime.html', errors=[str(error)])

    def create_game_level(self):
        '''
        Creates a new level in the database, the levels are basically a
        linked-list where each level points to the next, and the last points to
        None.  This function creates a new level and sorts everything based on
        the 'number' attrib
        '''
        try:
            new_level = GameLevel()
            new_level.number = self.get_argument('level_number', '')
            new_level.buyout = self.get_argument('buyout', 0)
            new_level.name = self.get_argument('name', None)
            new_level._type = self.get_argument('type', 'buyout')
            new_level._reward = self.get_argument('reward', 0)
            if new_level._type == "progress":
                new_level.buyout = min(new_level.buyout, 100)
            elif new_level._type == "none":
                new_level.buyout = 0
            if new_level._type != "none" and new_level.buyout == 0:
                new_level._type = "none"
            self.dbsession.add(new_level)
            self.dbsession.flush()
            game_levels = sorted(GameLevel.all())
            for index, level in enumerate(game_levels[:-1]):
                level.next_level_id = game_levels[index + 1].id
                self.dbsession.add(level)
            if game_levels[0].number != 0:
                game_levels[0].number = 0
            self.dbsession.add(game_levels[0])
            game_levels[-1].next_level_id = None
            self.dbsession.add(game_levels[-1])
            self.dbsession.commit()
            self.redirect('/admin/view/game_levels')
        except ValidationError as error:
            self.render('admin/create/game_level.html', errors=[str(error), ])

    def create_hint(self):
        ''' Add hint to database '''
        try:
            box = Box.by_uuid(self.get_argument('box_uuid', ''))
            if box is None:
                raise ValidationError("Box does not exist")
            hint = Hint(box_id=box.id)
            hint.price = self.get_argument('price', '')
            hint.description = self.get_argument('description', '')
            flag = Flag.by_uuid(self.get_argument('flag_uuid', ''))
            if flag:
                hint.flag_id = flag.id
            else:
                hint.flag_id = None
            self.dbsession.add(hint)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects#%s" % box.uuid)
        except ValidationError as error:
            self.render('admin/create/hint.html', errors=[str(error), ])

    def _mkflag(self, flag_type, is_file=False):
        ''' Creates the flag in the database '''
        box = Box.by_uuid(self.get_argument('box_uuid', ''))
        if box is None:
            raise ValidationError('Box does not exist')
        if is_file:
            if not hasattr(self.request, 'files') or not 'flag' in self.request.files:
                raise ValidationError('No file in request')
            token = self.request.files['flag'][0]['body']
        else:
            token = self.get_argument('token', '')
        name = self.get_argument('flag_name', '')
        description = self.get_argument('description', '')
        reward = self.get_argument('reward', '')
        flag = Flag.create_flag(
            flag_type, box, name, token, description, reward)
        flag.capture_message = self.get_argument('capture_message', '')
        flag.case_sensitive = self.get_argument('case-sensitive', 1)
        lock = Flag.by_uuid(self.get_argument('lock_uuid', ''))
        if lock:
            flag.lock_id = lock.id
        else:
            flag.lock_id = None
        self.add_attachments(flag)
        self.dbsession.add(flag)
        self.dbsession.commit()
        choices = self.get_arguments('addmore[]', strip=True)
        if choices is not None:
            for item in choices:
                FlagChoice.create_choice(flag, item)
        self.redirect("/admin/view/game_objects#%s" % box.uuid)

    def add_attachments(self, flag):
        ''' Add uploaded files as attachments to flags '''
        if hasattr(self.request, 'files'):
            if not 'attachments' in self.request.files:
                return
            for attachment in self.request.files['attachments']:
                flag_attachment = FlagAttachment(file_name=attachment['name'])
                flag_attachment.data = attachment['body']
                flag.attachments.append(flag_attachment)
                self.dbsession.add(flag_attachment)
            self.dbsession.flush()


class AdminViewHandler(BaseHandler):

    ''' View game objects '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Calls a view function based on URI '''
        uri = {
            'game_objects': "admin/view/game_objects.html",
            'game_levels': "admin/view/game_levels.html",
            'market_objects': 'admin/view/market_objects.html',
            'categories': 'admin/view/categories.html',
            'pastebin': 'admin/view/pastebin.html',
            'fileshare': 'admin/view/shared_files.html',
            'statistics': 'admin/view/statistics.html',
            'notifications': 'admin/view/notifications.html'
        }
        if len(args) and args[0] in uri:
            self.render(uri[args[0]], errors=None)
        else:
            self.render("public/404.html")


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
            'ipv4': 'game_objects',
            'ipv6': 'game_objects',
            'game_level': 'game_levels',
            'box_level': 'game_levels',
            'hint': 'game_objects',
            'market_item': 'market_objects',
            'category': 'categories',
        }
        if len(args) and args[0] in uri:
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
            'ip': self.edit_ip,
            'game_level': self.edit_game_level,
            'box_level': self.box_level,
            'hint': self.edit_hint,
            'market_item': self.edit_market_item,
            'category': self.edit_category,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def edit_corporations(self):
        ''' Updates corporation object in the database '''
        try:
            corp = Corporation.by_uuid(self.get_argument('uuid', ''))
            if corp is None:
                raise ValidationError("Corporation does not exist")
            name = self.get_argument('name', '')
            if name != corp.name:
                logging.info("Updated corporation name %s -> %s" % (
                    corp.name, name
                ))
                corp.name = name
                self.dbsession.add(corp)
                self.dbsession.commit()
            self.redirect('/admin/view/game_objects')
        except ValidationError as error:
            self.render("admin/view/game_objects.html", errors=[str(error), ])

    def edit_category(self):
        ''' Updates category object in the database '''
        try:
            cat = Category.by_uuid(self.get_argument('uuid', ''))
            if cat is None:
                raise ValidationError("Category does not exist")
            category = self.get_argument('category', '')
            if category != cat.category:
                logging.info("Updated category name %s -> %s" % (
                    cat.category, category
                ))
                cat.category = category
                self.dbsession.add(cat)
                self.dbsession.commit()
            self.redirect('/admin/view/categories')
        except ValidationError as error:
            self.render("admin/view/categories.html", errors=[str(error), ])

    def edit_boxes(self):
        '''
        Edit existing boxes in the database, and log the changes
        '''
        try:
            box = Box.by_uuid(self.get_argument('uuid', ''))
            if box is None:
                raise ValidationError("Box does not exist")
            # Name
            name = self.get_argument('name', '')
            if name != box.name:
                if Box.by_name(name) is None:
                    logging.info("Updated box name %s -> %s" % (
                        box.name, name,
                    ))
                    box.name = name
                else:
                    raise ValidationError("Box name already exists")
            # Corporation
            corp = Corporation.by_uuid(self.get_argument('corporation_uuid'))
            if corp is not None and corp.id != box.corporation_id:
                logging.info("Updated %s's corporation %s -> %s" % (
                    box.name, box.corporation_id, corp.id,
                ))
                box.corporation_id = corp.id
            elif corp is None:
                raise ValidationError("Corporation does not exist")
            # Category
            cat = Category.by_uuid(self.get_argument('category_uuid'))
            if cat is not None and cat.id != box.category_id:
                logging.info("Updated %s's category %s -> %s" % (
                    box.name, box.category_id, cat.id,
                ))
                box.category_id = cat.id
            elif cat is None and cat != box.category_id:
                logging.info("Updated %s's category %s -> None" % (
                    box.name, box.category_id,
                ))
                box.category_id = None
            # System Type
            ostype = self.get_argument('operating_system')
            if ostype is not None and ostype != box.operating_system:
                logging.info("Updated %s's system type %s -> %s" % (
                    box.name, box.operating_system, ostype,
                ))
                box.operating_system = ostype
            # Description
            description = self.get_argument('description', '')
            if description != box._description:
                logging.info("Updated %s's description %s -> %s" % (
                    box.name, box.description, description,
                ))
                box.description = description
            # Difficulty
            difficulty = self.get_argument('difficulty', '')
            if difficulty != box.difficulty:
                logging.info("Updated %s's difficulty %s -> %s" % (
                    box.name, box.difficulty, difficulty,
                ))
                box.difficulty = difficulty
            # Flag submission type
            flag_submission_type = self.get_argument('flag_submission_type', '')
            if flag_submission_type is not None and flag_submission_type != box.flag_submission_type:
                logging.info("Updated %s's flag submission type %s -> %s" % (
                    box.name, box.flag_submission_type, flag_submission_type
                ))
                box.flag_submission_type = flag_submission_type
            # Avatar
            avatar_select = self.get_argument('box_avatar_select', '')
            if avatar_select and len(avatar_select) > 0:
                box._avatar = avatar_select
            elif 'avatar' in self.request.files:
                box.avatar = self.request.files['avatar'][0]['body']

            self.dbsession.add(box)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects#%s" % box.uuid)
        except ValidationError as error:
            self.render("admin/view/game_objects.html", errors=[str(error), ])

    def edit_flags(self):
        ''' Edit existing flags in the database '''
        try:
            flag = Flag.by_uuid(self.get_argument('uuid', ''))
            if flag is None:
                raise ValidationError("Flag does not exist")
            # Name
            name = self.get_argument('name', '')
            if flag.name != name:
                logging.info("Updated flag name %s -> %s" % (
                    flag.name, name,
                ))
                flag.name = name
            token = self.get_argument('token', '')
            if flag.token != token:
                flag.token = token
            # Description
            description = self.get_argument('description', '')
            if flag._description != description:
                logging.info("Updated %s's description %s -> %s" % (
                    flag.name, flag._description, description,
                ))
                flag.description = description
            # Value
            flag.value = self.get_argument('value', '')
            flag.capture_message = self.get_argument('capture_message', '')
            flag.case_sensitive = self.get_argument('case-sensitive', 1)
            # Dependency Lock
            lock = Flag.by_uuid(self.get_argument('lock_uuid', ''))
            if lock:
                flag.lock_id = lock.id
            else:
                flag.lock_id = None
            box = Box.by_uuid(self.get_argument('box_uuid', ''))
            if box is not None and flag not in box.flags:
                logging.info("Updated %s's box %d -> %d" % (
                    flag.name, flag.box_id, box.id
                ))
                flag.box_id = box.id
            elif box is None:
                raise ValidationError("Box does not exist")
            self.dbsession.add(flag)
            self.dbsession.commit()
            if flag.type == FLAG_CHOICE:
                self.edit_choices(flag, self.request.arguments)
            self.redirect("/admin/view/game_objects#%s" % box.uuid)
        except ValidationError as error:
            self.render("admin/view/game_objects.html", errors=["%s" % error])

    def edit_choices(self, flag, arguments):
        ''' Edit flag multiple choice items '''
        choiceitems = {}
        currentchoices = json.loads(flag.choices())
        for item in arguments:
            if item.startswith("choice"):
                if arguments[item][0] != "":
                    uuidsplit = item.split("uuid-")
                    if len(uuidsplit) > 1:
                        choiceitems[uuidsplit[1]] = arguments[item][0]
                    else:
                        for flagoption in arguments[item]:
                            if flagoption != "":
                                # add choice
                                FlagChoice.create_choice(flag, flagoption)
        for choice in currentchoices:
            if not choice['uuid'] in choiceitems:
                # delete choice
                flagchoice = FlagChoice.by_uuid(choice['uuid'])
                self.dbsession.delete(flagchoice)
        for choice in choiceitems:
            flagchoice = FlagChoice.by_uuid(choice)
            if choiceitems[choice] != flagchoice.choice:
                # update choice
                flagchoice.choice = choiceitems[choice]
                self.dbsession.add(flagchoice)
        self.dbsession.commit()

    def edit_ip(self):
        ''' Add ip addresses to a box (sorta edits the box object) '''
        try:
            box = Box.by_uuid(self.get_argument('box_uuid', ''))
            if box is None:
                raise ValidationError("Box does not exist")
            ip_addr = self.get_argument('ip_address', '')
            if IpAddress.by_address(ip_addr) is None:
                ip = IpAddress(box_id=box.id, address=ip_addr)
                if self.get_argument('visable', '').lower() != 'true':
                    ip.visable = False
                box.ip_addresses.append(ip)
                self.dbsession.add(ip)
                self.dbsession.add(box)
                self.dbsession.commit()
                self.redirect("/admin/view/game_objects#%s" % box.uuid)
            else:
                raise ValidationError("IP address is already in use")
        except ValidationError as error:
            self.render("admin/view/game_objects.html", errors=[str(error), ])

    def edit_game_level(self):
        ''' Update game level objects '''
        try:
            level = GameLevel.by_uuid(self.get_argument('uuid', ''))
            if level is None:
                raise ValidationError("Game level does not exist")
            if int(self.get_argument('number', level.number)) != level.number:
                level.number = self.get_argument('number')
            level.buyout = self.get_argument('buyout', 1)
            level._type = self.get_argument('type', 'buyout')
            level._reward = self.get_argument('reward', 0)
            level.name = self.get_argument('name', None)
            if level._type == "progress":
                level.buyout = min(level.buyout, 100)
            elif level._type == "none":
                level.buyout = 0
            if level._type != "none" and level.buyout == 0:
                level._type = "none"
            self.dbsession.add(level)
            self.dbsession.flush()
            # Fix the linked-list
            game_levels = sorted(GameLevel.all())
            for index, game_level in enumerate(game_levels[:-1]):
                game_level.next_level_id = game_levels[index + 1].id
                self.dbsession.add(game_level)
            if game_levels[0].number != 0:
                game_levels[0].number = 0
            self.dbsession.add(game_levels[0])
            game_levels[-1].next_level_id = None
            self.dbsession.add(game_levels[-1])
            self.dbsession.add(level)
            self.dbsession.commit()
            self.redirect('/admin/view/game_levels')
        except ValueError:
            raise ValidationError("That was not a number ...")
        except ValidationError as error:
            self.render("admin/view/game_levels.html", errors=[str(error), ])

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
        try:
            hint = Hint.by_uuid(self.get_argument('uuid', ''))
            if hint is None:
                raise ValidationError("Hint does not exist")
            logging.debug("Edit hint object with uuid of %s" % hint.uuid)
            price = self.get_argument('price', '')
            if hint.price != price:
                hint.price = price
            description = self.get_argument('description', '')
            hint.description = description
            flag = Flag.by_uuid(self.get_argument('hint-flag_uuid', ''))
            if flag:
                flag_id = flag.id
            else:
                flag_id = None
            hint.flag_id = flag_id
            box = Box.by_id(flag.box_id)
            self.dbsession.add(hint)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects#%s" % box.uuid)
        except ValidationError as error:
            self.render("admin/view/game_objects.html", errors=[str(error), ])

    def edit_market_item(self):
        ''' Change a market item's price '''
        try:
            item = MarketItem.by_uuid(self.get_argument('item_uuid', ''))
            if item is None:
                raise ValidationError("Item does not exist")
            price = self.get_argument('price', item.price)
            if item.price != price:
                item.price = price
            self.dbsession.add(item)
            self.dbsession.commit()
            self.redirect('/admin/view/market_objects')
        except ValidationError as error:
            self.render('admin/view/market_objects.html', errors=[str(error)])


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
            'game_level': self.del_game_level,
            'category': self.del_category,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def del_ip(self):
        ''' Delete an ip address object '''
        ip = IpAddress.by_uuid(self.get_argument('ip_uuid', ''))
        if ip is not None:
            logging.info("Deleted IP address: '%s'" % str(ip))
            self.dbsession.delete(ip)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects")
        else:
            logging.info("IP address (%r) does not exist in database" % (
                self.get_argument('ip_uuid', ''),
            ))
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
            logging.info("Flag (%r) does not exist in the database" % (
                self.get_argument('uuid', '')
            ))
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

    def del_category(self):
        ''' Delete a category '''
        cat = Category.by_uuid(self.get_argument('uuid', ''))
        if cat is not None:
            logging.info("Delete category: %s" % cat.category)
            self.dbsession.delete(cat)
            self.dbsession.commit()
            self.redirect('/admin/view/categories')
        else:
            self.render('admin/view/categories.html',
                        errors=["Category does not exist in database."]
                        )

    def del_box(self):
        ''' Delete a box '''
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

    def del_game_level(self):
        ''' Deletes a game level, and fixes the linked list '''
        game_level = GameLevel.by_uuid(self.get_argument('uuid', ''))
        if game_level is not None:
            game_levels = sorted(GameLevel.all())
            game_levels.remove(game_level)
            for index, level in enumerate(game_levels[:-1]):
                level.next_level_id = game_levels[index + 1].id
                self.dbsession.add(level)
            if game_levels[0].number != 0:
                game_levels[0].number = 0
            self.dbsession.add(game_levels[0])
            game_levels[-1].next_level_id = None
            self.dbsession.add(game_levels[-1])
            self.dbsession.delete(game_level)
            self.dbsession.commit()
            self.redirect('/admin/view/game_levels')
        else:
            self.render('admin/view/game_levels.html',
                        errors=["Game level does not exist in database."]
                        )


class AdminAjaxGameObjectDataHandler(BaseHandler):

    ''' Handles AJAX data for admin handlers '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        game_objects = {
            'game_level': GameLevel,
            'corporation': Corporation,
            'flag': Flag,
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
        elif obj_name == "stats":
            flag = Flag.by_uuid(uuid)
            if flag is not None:
                if options.banking:
                    flaginfo = [{"name": flag.name, "token": flag.token, "price": "$" + str(flag.value)}]
                else:
                    flaginfo = [{"name": flag.name, "token": flag.token, "price": str(flag.value) + " points"}]
                captures = []
                for item in Flag.captures(flag.id):
                    team = Team.by_id(item[0])
                    if team:
                        captures.append({"name": team.name})
                attempts = []
                for item in Penalty.by_flag_id(flag.id):
                    team = Team.by_id(item.team_id)
                    if team:
                        attempts.append({"name": team.name, "token": item.token})
                hints = []
                for item in Hint.taken_by_flag(flag.id):
                    team = Team.by_id(item.team_id)
                    hint = Hint.by_id(item.hint_id)
                    if team:
                        if options.banking:
                            hints.append({"name": team.name, "price": "$" + str(hint.price)})
                        else:
                            hints.append({"name": team.name, "price": str(hint.price) + " points"})
                obj = {
                    "flag": flaginfo,
                    "captures": captures, 
                    "attempts": attempts, 
                    "hints": hints,
                    }
                self.write(obj)
            else:
                self.write({'Error': 'Invalid uuid.'})
        else:
            self.write({'Error': 'Invalid object type.'})
        self.finish()


class AdminTestTokenHandler(BaseHandler):

    ''' Handles token test '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        token = self.get_argument('token', '')
        submission = self.get_argument('submission', '')
        flagtype = self.get_argument('flagtype', 'static')
        case = int(self.get_argument('case', 1))
        if flagtype == FLAG_STATIC:
            if case == 0:
                test = str(token).lower().strip() == str(submission).lower().strip()
            else:
                test = str(token).strip() == str(submission).strip()
        elif flagtype == FLAG_REGEX:
            if not token.startswith("^(") and not token.endswith(")$"):
                token = "^(" + token + ")$"
            if case == 0:
                pattern = re.compile(token, re.IGNORECASE)
            else:
                pattern = re.compile(token)
            test = pattern.match(submission) is not None
        elif flagtype == FLAG_DATETIME:
            from dateutil.parser import parse
            try:
                test = parse(token) == parse(submission)
            except:
                test = False
        else:
            self.write({'Error': 'Invalid flag type, cannot capture'})
        if test is not None:
            self.write({'Success': test})
        else:
            self.write({'Error': 'Invalid submission.'})
        self.finish()
