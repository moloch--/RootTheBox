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
from models.Penalty import Penalty
from libs.SecurityDecorators import authenticated
from handlers.BaseHandlers import BaseHandler


class FirstLoginHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        reward = self.config.bot_reward
        usebots = self.config.use_bots
        banking = self.config.banking
        self.add_content_policy('script', "'unsafe-eval'")
        self.render('missions/firstlogin.html', reward=reward, user=user, bots=usebots, bank=banking)


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
                        success=[],
                        info=[])
        else:
            self.render('public/404.html')


class FlagSubmissionHandler(BaseHandler):

    @authenticated
    def post(self, *args, **kwargs):
        ''' Check validity of flag submissions '''
        flag = Flag.by_uuid(self.get_argument('uuid', ''))
        user = self.get_current_user()
        if flag and flag in user.team.flags:
            self.render_page(flag)
        elif flag is not None and flag.game_level in user.team.game_levels:
            submission = ''
            if flag.is_file:
                if hasattr(self.request, 'files') and 'flag' in self.request.files:
                    submission = self.request.files['flag'][0]['body']
            else:
                submission = self.get_argument('token', '')
            old_reward = flag.value

            if self.attempt_capture(flag, submission):
                self.add_content_policy('script', "'unsafe-eval'")
                if self.config.story_mode:
                    self.render('missions/captured.html',
                                flag=flag,
                                reward=old_reward)
                else:
                    success = self.success_capture(flag)
                    self.render_page(flag, success=success)
            else:
                if Penalty.by_token_count(flag, user.team, submission) == 0:
                    if self.config.teams:
                        teamval = "team's "
                    else:
                        teamval = ""
                    penalty = self.failed_capture(flag, submission)
                    penalty_dialog = "Sorry - Try Again"
                    if penalty:
                        if self.config.banking:
                            penalty_dialog = "$" + str(penalty) + " has been deducted from your " + teamval + "account."
                        else:
                            if penalty == 1:
                                point = " point has"
                            else:
                                point = " points have"
                            penalty_dialog = str(penalty) + point + " been deducted from your " + teamval + "score."
                    self.render_page(flag, errors=[penalty_dialog])
                else:
                    if self.config.teams:
                        teamdup = " by your team.  Try Again"
                    else:
                        teamdup = " by you.  Try Again"
                    self.render_page(flag, info=["Duplicate submission - this answer has already been attempted" + teamdup])
        else:
            self.render('public/404.html')

    def success_capture(self, flag):
        if self.config.teams:
            teamval = "team's "
        else:
            teamval = ""
        user = self.get_current_user()
        old_reward = flag.value
        reward_dialog = flag.name + " answered correctly. "
        if self.config.banking:
            reward_dialog += "$" + str(old_reward) + " has been added to your " + teamval + "account."
        else:
            reward_dialog += str(old_reward) + " points added to your " + teamval + "score."
        success = [reward_dialog]

        # Check for Box Completion
        boxcomplete = True
        box = flag.box
        for boxflag in box.flags:
            if not boxflag in user.team.flags:
                boxcomplete = False
                break
        if boxcomplete:
            success.append("Congratulations! You have completed " + box.name + ".")

        # Check for Level Completion
        level = GameLevel.by_id(box.game_level_id)
        level_progress = len(user.team.level_flags(level.number)) /  float(len(level.flags))
        if level_progress == 1.0 and level not in user.team.game_levels:
            reward_dialog = ""
            if level._reward > 0:
                user.team.money += level._reward
                self.dbsession.add(user.team)
                self.dbsession.flush()
                self.dbsession.commit()
                if self.config.banking:
                    reward_dialog += "$" + str(level._reward) + " has been added to your " + teamval + "account."
                else:
                    reward_dialog += str(level._reward) + " points added to your " + teamval + "score."
            success.append("Congratulations! You have completed " + str(level.name) + ". " + reward_dialog)

        # Unlock next level if based on Game Progress
        next_level = GameLevel.by_id(level.next_level_id)
        if next_level._type == "progress" and level_progress * 100 >= next_level.buyout and next_level not in user.team.game_levels:
            logging.info("%s (%s) unlocked %d" % (
                    user.handle, user.team.name, next_level.name
                ))
            user.team.game_levels.append(next_level)
            self.dbsession.add(user.team)
            self.dbsession.commit()
            self.event_manager.level_unlocked(user, next_level)
            success.append("Congratulations! You have unlocked " + str(next_level.name))
        
        return success

    def failed_capture(self, flag, submission):
        user = self.get_current_user()
        if submission is not None and flag not in user.team.flags:
            if flag.is_file:
                submission = Flag.digest(submission)
            Penalty.create_attempt(
                team=user.team,
                flag=flag,
                submission=submission,
            )
            if not self.config.penalize_flag_value:
                return False
            attempts = Penalty.by_count(flag, user.team)
            if attempts < self.config.flag_start_penalty:
                return False
            if attempts >= self.config.flag_stop_penalty:
                return False
            penalty = int(flag.value * self.config.flag_penalty_cost * .01)
            logging.info("%s (%s) capture failed '%s' - lost %s" % (
                user.handle, user.team.name, flag.name, penalty
            ))
            user.team.money -= penalty
            user.money -= penalty
            self.dbsession.add(user.team)
            self.dbsession.flush()
            self.event_manager.flag_penalty(user, flag)
            self.dbsession.commit()
            return penalty
        return False

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
                user.money += flag.value
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

    def render_page(self, flag, errors=[], success=[], info=[]):
        ''' Wrapper to .render() to avoid duplicate code '''
        user = self.get_current_user()
        box = Box.by_id(flag.box_id)
        self.render('missions/box.html',
                    box=box,
                    team=user.team,
                    errors=errors,
                    success=success,
                    info=info)


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

    def render_page(self, box, errors=[], success=[], info=[]):
        ''' Wrapper to .render() to avoid duplicate code '''
        user = self.get_current_user()
        self.render('missions/box.html',
                    box=box,
                    team=user.team,
                    errors=errors,
                    success=success,
                    info=info)


class MissionsHandler(BaseHandler):

    ''' Renders pages related to Missions/Flag submissions '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Render missions view '''
        user = self.get_current_user()
        self.render("missions/view.html", team=user.team, errors=None, success=None)

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
                logging.info("%s (%s) payed buyout for %d" % (
                    user.handle, user.team.name, level.name
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
                            errors=["You do not have enough money to unlock this level"],
                            success=None)
        else:
            self.render("missions/view.html",
                        team=user.team,
                        errors=["Level does not exist"],
                        success=None)
