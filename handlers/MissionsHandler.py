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

from models.GameLevel import GameLevel
from models.Flag import Flag
from models.Box import Box
from models.Hint import Hint
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler


class FirstLoginHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        reward = self.config.bot_reward
        self.add_content_policy('script', "'unsafe-eval'")
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
                        errors=[])
        else:
            self.render('public/404.html')


class FlagSubmissionHandler(BaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        ''' Check validity of flag submissions '''
        flag = Flag.by_uuid(self.get_argument('uuid', ''))
        user = self.get_current_user()
        if flag is not None and flag.game_level in user.team.game_levels:
            submission = ''
            if flag.is_file:
                if hasattr(self.request, 'files') and 'flag' in self.request.files:
                    submission = self.request.files['flag'][0]['body']
            else:
                submission = self.get_argument('token', '')
            old_reward = flag.value
            if self.attempt_capture(flag, submission):
                self.add_content_policy('script', "'unsafe-eval'")
                self.render('missions/captured.html',
                            flag=flag,
                            reward=old_reward)
            else:
                self.render_page(flag, errors=["Invalid flag submission"])
        else:
            self.render('public/404.html')

    def attempt_capture(self, flag, submission):
        ''' Compares a user provided token to the token in the db '''
        user = self.get_current_user()
        logging.info("%s (%s) capture the flag '%s'" % (
            user.handle, user.team.name, flag.name
        ))
        if submission is not None and flag not in user.team.flags:
            if flag.capture(submission):
                user.team.flags.append(flag)
                user.team.money += flag.value
                self.dbsession.add(user.team)
                if self.config.dynamic_flag_value:
                    depreciation = float(1.0 / self.config.flag_value_decrease)
                    flag.value -= int(flag.value * depreciation)
                self.dbsession.add(flag)
                self.dbsession.flush()
                self.event_manager.flag_captured(user, flag)
                self._check_level(flag)
                self.dbsession.commit()
                return True
        return False

    def _check_level(self, flag):
        user = self.get_current_user()
        if len(user.team.level_flags(flag.game_level.number)) == len(flag.game_level.flags):
            next_level = flag.game_level.next()
            logging.info("Next level is %r" % next_level)
            if next_level is not None and next_level not in user.team.game_levels:
                logging.info("Team completed level, unlocking the next level")
                user.team.game_levels.append(next_level)
                self.dbsession.add(user.team)

    def render_page(self, flag, errors=[]):
        ''' Wrapper to .render() to avoid duplicate code '''
        user = self.get_current_user()
        box = Box.by_id(flag.box_id)
        self.render('missions/box.html',
                    box=box,
                    team=user.team,
                    errors=errors)


class PurchaseHintHandler(BaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        ''' Purchase a hint '''
        uuid = self.get_argument('uuid', '')
        hint = Hint.by_uuid(uuid)
        if hint is not None:
            user = self.get_current_user()
            if hint.price <= user.team.money:
                logging.info("%s (%s) purchased a hint for $%d on %s" % (
                    user.handle, user.team.name, hint.price, hint.box.name
                ))
                self._purchase_hint(hint, user.team)
                self.render_page(hint.box)
            else:
                self.render_page(
                    hint.box, ["You cannot afford to purchase this hint."])
        else:
            self.render('public/404.html')

    def _purchase_hint(self, hint, team):
        ''' Add hint to team object '''
        if hint not in team.hints:
            team.money -= abs(hint.price)
            team.hints.append(hint)
            self.dbsession.add(team)
            self.dbsession.commit()

    def render_page(self, box, errors=[]):
        ''' Wrapper to .render() to avoid duplicate code '''
        user = self.get_current_user()
        self.render('missions/box.html',
                    box=box,
                    team=user.team,
                    errors=errors)


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
        if len(args) and args[0] in uri:
            uri[str(args[0])]()
        else:
            self.render("public/404.html")

    def buyout(self):
        ''' Buyout and unlock a level '''
        user = self.get_current_user()
        level = GameLevel.by_uuid(self.get_argument('uuid', ''))
        if level is not None and user is not None:
            if level.buyout <= user.team.money:
                logging.info("%s (%s) payed buyout for level #%d" % (
                    user.handle, user.team.name, level.number
                ))
                user.team.game_levels.append(level)
                user.team.money -= level.buyout
                self.dbsession.add(user.team)
                self.dbsession.commit()
                self.event_manager.level_unlocked(user, level)
                self.redirect("/user/missions")
            else:
                self.render("missions/view.html",
                            team=user.team,
                            errors=["You do not have enough money to unlock this level"])
        else:
            self.render("missions/view.html",
                        team=user.team,
                        errors=["Level does not exist"]
                        )
