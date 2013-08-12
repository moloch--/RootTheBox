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

from models import dbsession, GameLevel, Flag, Box
from libs.Form import Form
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler


class FirstLoginHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        self.render('missions/firstlogin.html', user=user)


class BoxHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        uuid = self.get_argument('uuid', '')
        box = Box.by_uuid(uuid)
        user = self.get_current_user()
        self.render('missions/box.html', box=box, team=user.team)


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
        uri = {
            'flag': self.flag,
            'buyout': self.buyout,
        }
        if len(args) == 1 and args[0] in uri:
            uri[str(args[0])]()
        else:
            self.render("public/404.html")

    def flag(self):
        '''
        Accepts flag submissions, a flag can be either a string or a file,
        if the flag submission is a file the MD5 hexdigest is used.
        '''
        form = Form(flag_type="Missing flag type")
        user = self.get_current_user()
        if form.validate(self.request.arguments):
            flag = Flag.by_uuid(self.get_argument('uuid', ''))
            if flag is not None:
                if self.get_argument('flag_type').lower() == 'text':
                    token = self.get_argument('token', None)
                    errors = self.__chkflag__(flag, token)
                    if len(errors) == 0:
                        self.flag_captured()
                    else:
                        self.render("missions/view.html",
                            team=user.team,
                            errors=errors
                        )
                elif self.get_argument('flag_type').lower() == 'file':
                    if 0 < len(self.request.files['flag'][0]['body']):
                        file_data = self.request.files['flag'][0]['body']
                        errors = self.__chkflag__(flag, file_data)
                        if len(errors) == 0:
                            self.flag_captured()
                        else:
                            self.render("missions/view.html",
                                team=user.team,
                                errors=errors
                            )
                    else:
                        logging.info("No file data in flag submission.")
                        self.render("missions/view.html",
                            team=user.team,
                            errors=["No file data"]
                        )
                else:
                    self.render("missions/view.html",
                        team=user.team,
                        errors=["Invalid flag type"]
                    )
            else:
                self.render("missions/view.html",
                    team=user.team,
                    errors=["Flag does not exist"]
                )
        else:
            self.render("missions/view.html",
                team=user.team,
                errors=form.errors
            )

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

    def flag_captured(self):
        ''' 
        Successfully captured flag, checks for if level has been completed 
        and redirects user back to the missions page.
        '''
        self.__chklevel__()
        self.redirect("/user/missions")

    def __chkflag__(self, flag, user_token):
        ''' Compares a user provided token to the token in the db '''
        user = self.get_current_user()
        if user_token is not None and flag == user_token:
            user.team.flags.append(flag)
            user.team.money += flag.value
            dbsession.add(user.team)
            flag.value = int(flag.value * 0.90)
            dbsession.add(flag)
            dbsession.flush()
            event = self.event_manager.create_flag_capture_event(user, flag)
            self.new_events.append(event)
            return []
        else:
            return ["Invalid flag submission"]

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