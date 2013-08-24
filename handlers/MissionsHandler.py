# -*- coding: utf-8 -*-
'''
Created on Oct 28, 2012

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

This file contains the code for displaying flags / recv flag submissions

'''


import logging
import hashlib

from models import dbsession, Box, Hint, Flag
from libs.Form import Form
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler


class FirstLoginHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        reward = self.config.bot_reward
        self.render('missions/firstlogin.html', reward=reward, user=user)


class BoxHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' 
        Renders the box details page.
        '''
        uuid = self.get_argument('uuid', '')
        box = Box.by_uuid(uuid)
        if box is not None:
            user = self.get_current_user()
            self.render('missions/box.html', 
                box=box, 
                team=user.team,
                errors=[],
            )
        else:
            self.render('public/404.html')


class FlagSubmissionHandler(BaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        ''' Check validity of flag submissions '''
        flag = Flag.by_uuid(self.get_argument('uuid', ''))
        if flag is not None:
            if flag.is_file:
                self.validate_file(flag)
            else:
                self.validate_text(flag)
        else:
            self.render('public/404.html')

    def validate_text(self, flag):
        ''' Check a text submission '''
        token = self.get_argument('token', '')
        if self.capture(flag, token):
            self.render_page(flag)
        else:
            self.render_page(flag, errors=["Invalid flag submission."])

    def validate_file(self, flag):
        ''' Check a file submission '''
        if 0 < len(self.request.files['flag'][0]['body']):
            file_data = self.request.files['flag'][0]['body']
            digest = Flag.digest(file_data)
            if self.capture(flag, digest):
                self.render_page(flag)
            else:
                self.render_page(flag, errors=["Invalid flag submission."])
        else:
            self.render_page(flag, errors=["Missing flag data."])


    def capture(self, flag, user_token):
        ''' Compares a user provided token to the token in the db '''
        user = self.get_current_user()
        if flag.token == user_token:
            user.team.flags.append(flag)
            user.team.money += flag.value
            dbsession.add(user.team)
            flag.value = int(flag.value * 0.90)
            dbsession.add(flag)
            dbsession.flush()
            event = self.event_manager.create_flag_capture_event(user, flag)
            self.new_events.append(event)
            return True
        else:
            return False

    def render_page(self, flag, errors=[]):
        ''' Wrapper to .render() to avoid duplicate code '''
        user = self.get_current_user()
        box = Box.by_id(flag.box_id)
        self.render('missions/box.html', 
            box=box, 
            team=user.team,
            errors=errors,
        )


class PurchaseHintHandler(BaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        ''' Purchase a hint '''
        uuid = self.get_argument('uuid', '')
        hint = Hint.by_uuid(uuid)
        box = Box.by_id(hint.box_id)
        if hint is not None:
            user = self.get_current_user()
            if hint.price <= user.team.money:
                self._purchase_hint(hint, user.team)
                self.render_page(box)
            else:
                self.render_page(box, ["You cannot afford to purchase this hint."])
        else:
            self.render_page(box, ["Hint does not exist."])

    def _purchase_hint(self, hint, team):
        ''' Add hint to team object '''
        team.money -= hint.price
        team.hints.append(hint)
        dbsession.add(team)
        dbsession.flush()

    def render_page(self, box, errors=[]):
        ''' Wrapper to .render() to avoid duplicate code '''
        user = self.get_current_user()
        self.render('missions/box.html', 
            box=box, 
            team=user.team,
            errors=errors,
        )


class MissionsHandler(BaseHandler):
    ''' Renders pages related to Missions/Flag submissions '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Render missions view '''
        user = self.get_current_user()
        self.render("missions/view.html", team=user.team, errors=None)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Submit flags/buyout to levels '''
        uri = {'buyout': self.buyout}
        if len(args) == 1 and args[0] in uri:
            uri[str(args[0])]()
        else:
            self.render("public/404.html")

    def buyout(self):
        ''' Buyout and unlock a level '''
        form = Form(uuid="Level parameter missing")
        user = self.get_current_user()
        if form.validate(self.request.arguments):
            level = GameLevel.by_uuid(self.get_argument('uuid', ''))
            if level is not None and user is not None:
                if level.buyout < user.team.money:
                    user.team.game_levels.append(level)
                    user.team.money -= level.buyout
                    dbsession.add(user.team)
                    event = self.event_manager.create_unlocked_level_event(user, level)
                    self.new_events.append(event)
                    self.redirect("/user/missions")
                else:
                    self.render("missions/view.html",
                        team=user.team,
                        errors=[
                            "You do not have enough money to unlock this level"
                        ]
                    )
            else:
                self.render("missions/view.html",
                    team=user.team,
                    errors=["Level does not exist"]
                )
        else:
            self.render("missions/view.html",
                team=user.team,
                errors=form.errors
            )


    def __chklevel__(self):
        user = self.get_current_user()
        level = user.team.game_levels[-1]
        logging.info("%s completed %d of %d flags on level %d." % (
                user.team.name, len(user.team.level_flags(level.number)), 
                len(level.flags), level.number,
            )
        )
        if len(user.team.level_flags(level.number)) == len(level.flags):
            logging.info("%s has completed level #%d" % (user.team.name, level.number,))
            if level.next_level_id is not None:
                next_level = GameLevel.by_id(level.next_level_id)
                user.team.game_levels.append(next_level)
                dbsession.add(user.team)
                dbsession.flush()
                event = self.event_manager.create_unlocked_level_event(user, level)
                self.new_events.append(event)