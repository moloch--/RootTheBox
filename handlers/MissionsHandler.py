# -*- coding: utf-8 -*-
"""
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

"""


import logging
import json

from tornado.options import options
from builtins import next
from builtins import str
from past.utils import old_div
from libs.SecurityDecorators import authenticated, game_started
from libs.StringCoding import decode, encode
from libs.WebhookHelpers import *
from handlers.BaseHandlers import BaseHandler
from models.GameLevel import GameLevel
from models.Flag import Flag
from models.Team import Team
from models.Box import Box, FlagsSubmissionType
from models.Hint import Hint
from models.Penalty import Penalty


class FirstLoginHandler(BaseHandler):
    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        reward = self.config.bot_reward
        usebots = self.config.use_bots
        banking = self.config.banking
        self.add_content_policy("script", "'unsafe-eval'")
        self.render(
            "missions/firstlogin.html",
            reward=reward,
            user=user,
            bots=usebots,
            bank=banking,
        )


class StoryAjaxHandler(BaseHandler):
    @authenticated
    def get(self, *args, **kargs):
        """ Renders AJAX snippit based on URI """
        uri = {"firstlogin": self.firstlogin}
        user = self.get_current_user()
        if user and len(args) and args[0] in uri:
            dialog = uri[args[0]]()
            if isinstance(options.story_signature, list):
                dialog.extend(options.story_signature)
            for index, line in enumerate(dialog):
                try:
                    dialog[index] = line.replace("$user", str(user.handle)).replace(
                        "$reward", str(options.bot_reward)
                    )
                except:
                    dialog[index] = line.replace("$user", encode(user.handle)).replace(
                        "$reward", ("%d" % options.bot_reward)
                    )
            dialog.append(" ")
            try:
                self.write(json.dumps(dialog))
            except:
                self.write(json.dumps(dialog, encoding="latin1"))
        else:
            self.render("public/404.html")

    def firstlogin(self):
        """ Render the first login dialog """
        dialog = []
        if isinstance(options.story_firstlogin, list):
            dialog.extend(options.story_firstlogin)
        if options.use_bots and isinstance(options.story_bots, list):
            dialog.extend(options.story_bots)
        if options.banking and isinstance(options.story_banking, list):
            dialog.extend(options.story_banking)
        return dialog


class BoxHandler(BaseHandler):
    @authenticated
    @game_started
    def get(self, *args, **kwargs):
        """
        Renders the box details page.
        """
        uuid = self.get_argument("uuid", "")
        box = Box.by_uuid(uuid)
        if box is not None:
            user = self.get_current_user()
            level = GameLevel.by_id(box.game_level_id)
            if (
                user.team
                and level.type != "none"
                and level not in user.team.game_levels
            ):
                self.redirect("/403")
            elif box.locked:
                self.render(
                    "missions/status.html",
                    errors=None,
                    info=["This box is currently locked by the Admin."],
                )
            elif level.type == "locked":
                self.render(
                    "missions/status.html",
                    errors=None,
                    info=["This level is currently locked by the Admin."],
                )
            else:
                self.render(
                    "missions/box.html",
                    box=box,
                    user=user,
                    team=user.team,
                    errors=[],
                    success=[],
                    info=[],
                )
        else:
            self.render("public/404.html")

    @authenticated
    @game_started
    def post(self, *args, **kwargs):
        """ Check validity of flag submissions """
        box_id = self.get_argument("box_id", None)
        uuid = self.get_argument("uuid", "")
        token = self.get_argument("token", "")
        user = self.get_current_user()
        if (box_id and Box.by_id(box_id).locked) or (
            box_id is None and uuid and Flag.by_uuid(uuid).box.locked
        ):
            self.render(
                "missions/status.html",
                errors=None,
                info=["This box is currently locked by the Admin."],
            )
            return
        if (
            token is not None
            and box_id is not None
            and Box.by_id(box_id).flag_submission_type
            == FlagsSubmissionType.SINGLE_SUBMISSION_BOX
        ):
            flag = Flag.by_token_and_box_id(token, box_id)
        else:
            flag = Flag.by_uuid(uuid)
            if (
                flag is not None
                and Penalty.by_count(flag, user.team) >= self.config.max_flag_attempts
            ):
                self.render_page_by_flag(
                    flag,
                    info=["Max attempts reached - you can no longer answer this flag."],
                )
                return
        if flag and flag in user.team.flags:
            self.render_page_by_flag(flag)
            return
        elif (
            flag is None
            or flag.game_level.type == "none"
            or flag.game_level in user.team.game_levels
        ):
            submission = ""
            if flag is not None and flag.is_file:
                if hasattr(self.request, "files") and "flag" in self.request.files:
                    submission = self.request.files["flag"][0]["body"]
            else:
                submission = self.get_argument("token", "").replace("__quote__", '"')
            if len(submission) == 0:
                self.render_page_by_flag(
                    flag, info=["No flag was provided - try again."]
                )
                return
            old_reward = flag.dynamic_value(user.team) if flag is not None else 0
            if flag is not None and self.attempt_capture(flag, submission):
                self.add_content_policy("script", "'unsafe-eval'")
                success = self.success_capture(flag, old_reward)
                if self.config.story_mode:
                    box = flag.box
                    if not (len(box.capture_message) > 0 and box.is_complete(user)):
                        box = None
                    has_capture_message = (
                        len(flag.capture_message) > 0 or box is not None
                    )
                    if has_capture_message:
                        self.render(
                            "missions/captured.html",
                            flag=flag,
                            box=box,
                            reward=old_reward,
                            success=success,
                        )
                        return
                self.render_page_by_flag(flag, success=success)
                return
            else:
                self.failed_attempt(flag, user, submission, box_id)
        else:
            self.render("public/404.html")

    def failed_attempt(self, flag, user, submission, box_id):
        if flag is None or Penalty.by_token_count(flag, user.team, submission) == 0:
            if self.config.teams:
                teamval = "team's "
            else:
                teamval = ""
            penalty = self.failed_capture(flag, submission) if flag is not None else 0
            penalty_dialog = "Sorry - Try Again"
            if penalty:
                if self.config.banking:
                    penalty_dialog = (
                        "$"
                        + str(penalty)
                        + " has been deducted from your "
                        + teamval
                        + "account."
                    )
                else:
                    if penalty == 1:
                        point = " point has"
                    else:
                        point = " points have"
                    penalty_dialog = (
                        str(penalty)
                        + point
                        + " been deducted from your "
                        + teamval
                        + "score."
                    )
            if flag is None:
                self.render_page_by_box_id(box_id, errors=[penalty_dialog])
            else:
                self.render_page_by_flag(flag, errors=[penalty_dialog])
            return
        else:
            if self.config.teams:
                teamdup = " by your team.  Try Again"
            else:
                teamdup = " by you.  Try Again"
            self.render_page_by_flag(
                flag,
                info=[
                    "Duplicate submission - this answer has already been attempted"
                    + teamdup
                ],
            )
            return

    def success_capture(self, flag, old_reward=None):
        if self.config.teams:
            teamval = "team's "
        else:
            teamval = ""
        user = self.get_current_user()
        old_reward = flag.dynamic_value(user.team) if old_reward is None else old_reward
        reward_dialog = flag.name + " answered correctly. "
        if self.config.banking:
            reward_dialog += (
                "$"
                + str(old_reward)
                + " has been added to your "
                + teamval
                + "account."
            )
        else:
            reward_dialog += (
                str(old_reward) + " points added to your " + teamval + "score."
            )
        success = [reward_dialog]

        # Fire capture webhook
        send_capture_webhook(user, flag, old_reward)

        # Check for Box Completion
        box = flag.box
        if box.is_complete(user):
            if box.value > 0:
                user.team.money += box.value
                self.dbsession.add(user.team)
                self.dbsession.flush()
                self.dbsession.commit()
                dialog = str(box.value) + " points added to your " + teamval + "score."
                reward_dialog += dialog
                success.append(
                    "Congratulations! You have completed " + box.name + ". " + dialog
                )

                # Fire box complete webhook
                send_box_complete_webhook(user, box)
            else:
                success.append("Congratulations! You have completed " + box.name + ".")

        # Check for Level Completion
        level = GameLevel.by_id(box.game_level_id)
        level_progress = old_div(
            len(user.team.level_flags(level.number)), float(len(level.flags))
        )
        if level_progress == 1.0 and level not in user.team.game_levels:
            reward_dialog = ""
            if level._reward > 0:
                user.team.money += level._reward
                self.dbsession.add(user.team)
                self.dbsession.flush()
                self.dbsession.commit()
                if self.config.banking:
                    reward_dialog += (
                        "$"
                        + str(level._reward)
                        + " has been added to your "
                        + teamval
                        + "account."
                    )
                else:
                    reward_dialog += (
                        str(level._reward)
                        + " points added to your "
                        + teamval
                        + "score."
                    )
            success.append(
                "Congratulations! You have completed "
                + level.name
                + ". "
                + reward_dialog
            )

            # Fire level complete webhook
            send_level_complete_webhook(user, level)

        # Unlock level if based on Game Score
        for lv in GameLevel.all():
            if (
                lv.type == "points"
                and lv.buyout <= user.team.money
                and lv not in user.team.game_levels
            ):
                logging.info(
                    "%s (%s) unlocked %s" % (user.handle, user.team.name, lv.name)
                )
                user.team.game_levels.append(lv)
                self.dbsession.add(user.team)
                self.dbsession.commit()
                self.event_manager.level_unlocked(user, lv)
                success.append("Congratulations! You have unlocked " + lv.name)

        # Unlock next level if based on Game Progress
        next_level = GameLevel.by_id(level.next_level_id)
        if next_level and next_level not in user.team.game_levels:
            if level_progress == 1.0 or (
                next_level._type == "progress"
                and level_progress * 100 >= next_level.buyout
            ):
                logging.info(
                    "%s (%s) unlocked %s"
                    % (user.handle, user.team.name, next_level.name)
                )
                user.team.game_levels.append(next_level)
                self.dbsession.add(user.team)
                self.dbsession.commit()
                self.event_manager.level_unlocked(user, next_level)
                success.append("Congratulations! You have unlocked " + next_level.name)
        self.event_manager.push_score_update()
        return success

    def failed_capture(self, flag, submission):
        user = self.get_current_user()
        if submission is not None and flag not in user.team.flags:
            if flag.is_file:
                submission = Flag.digest(submission)
            Penalty.create_attempt(team=user.team, flag=flag, submission=submission)
            if not self.config.penalize_flag_value:
                return False
            attempts = Penalty.by_count(flag, user.team)
            if attempts < self.config.flag_start_penalty:
                return False
            if attempts >= self.config.flag_stop_penalty:
                return False
            penalty = int(
                flag.dynamic_value(user.team) * self.config.flag_penalty_cost * 0.01
            )
            logging.info(
                "%s (%s) capture failed '%s' - lost %s"
                % (user.handle, user.team.name, flag.name, penalty)
            )
            user.team.money -= penalty
            user.money -= penalty
            self.dbsession.add(user.team)
            self.dbsession.flush()
            self.event_manager.flag_penalty(user, flag)
            self.dbsession.commit()

            # Fire capture failed webhook
            send_capture_failed_webhook(user, flag)

            return penalty
        return False

    def attempt_capture(self, flag, submission):
        """ Compares a user provided token to the token in the db """
        user = self.get_current_user()
        team = user.team
        logging.info(
            "%s (%s) capture the flag '%s'" % (user.handle, team.name, flag.name)
        )
        if submission is not None and flag not in team.flags:
            if flag.capture(submission):
                flag_value = flag.dynamic_value(team)
                if (
                    self.config.dynamic_flag_value
                    and self.config.dynamic_flag_type == "decay_all"
                ):
                    for item in Flag.team_captures(flag.id):
                        tm = Team.by_id(item[0])
                        deduction = flag.dynamic_value(tm) - flag_value
                        tm.money = int(tm.money - deduction)
                        self.dbsession.add(tm)
                        self.event_manager.flag_decayed(tm, flag)
                team.money += flag_value
                user.money += flag_value
                team.flags.append(flag)
                user.flags.append(flag)
                self.dbsession.add(user)
                self.dbsession.add(team)
                self.dbsession.commit()
                self.event_manager.flag_captured(user, flag)
                return True
        return False

    def render_page_by_flag(self, flag, errors=[], success=[], info=[]):
        self.render_page_by_box_id(flag.box_id, errors, success, info)

    def render_page_by_box_id(self, box_id, errors=[], success=[], info=[]):
        box = Box.by_id(box_id)
        self.render_page_by_box(box, errors, success, info)

    def render_page_by_box(self, box, errors=[], success=[], info=[]):
        """ Wrapper to .render() to avoid duplicate code """
        user = self.get_current_user()
        self.render(
            "missions/box.html",
            box=box,
            user=user,
            team=user.team,
            errors=errors,
            success=success,
            info=info,
        )


class FlagCaptureMessageHandler(BaseHandler):
    @authenticated
    @game_started
    def get(self, *args, **kwargs):
        fuuid = self.get_argument("flag", None)
        buuid = self.get_argument("box", None)
        try:
            reward = int(self.get_argument("reward", 0))
        except ValueError:
            reward = 0
        user = self.get_current_user()
        box = Box.by_uuid(buuid)
        flag = Flag.by_uuid(fuuid)
        if box is not None and box.is_complete(user):
            if self.config.story_mode and len(box.capture_message) > 0:
                self.add_content_policy("script", "'unsafe-eval'")
                self.render("missions/captured.html", box=box, flag=None, reward=reward)
                return
        elif flag is not None and flag in user.team.flags:
            if self.config.story_mode and len(flag.capture_message) > 0:
                self.add_content_policy("script", "'unsafe-eval'")
                self.render(
                    "missions/captured.html", box=None, flag=flag, reward=reward
                )
                return
        self.render("public/404.html")


class PurchaseHintHandler(BaseHandler):
    @authenticated
    @game_started
    def post(self, *args, **kwargs):
        """ Purchase a hint """
        uuid = self.get_argument("uuid", "")
        hint = Hint.by_uuid(uuid)
        if hint is not None:
            user = self.get_current_user()
            flag = hint.flag
            if (
                flag
                and flag.box.flag_submission_type
                != FlagsSubmissionType.SINGLE_SUBMISSION_BOX
                and Penalty.by_count(flag, user.team) >= self.config.max_flag_attempts
            ):
                self.render_page(
                    hint.box, info=["You can no longer purchase this hint."]
                )
            elif hint.price <= user.team.money:
                logging.info(
                    "%s (%s) purchased a hint for $%d on %s"
                    % (user.handle, user.team.name, hint.price, hint.box.name)
                )
                self._purchase_hint(hint, user.team)
                self.render_page(hint.box)
            else:
                self.render_page(
                    hint.box, info=["You cannot afford to purchase this hint."]
                )
        else:
            self.render("public/404.html")

    def _purchase_hint(self, hint, team):
        """ Add hint to team object """
        if hint not in team.hints:
            user = self.get_current_user()
            team.money -= abs(hint.price)
            team.hints.append(hint)
            self.dbsession.add(team)
            self.dbsession.commit()
            self.event_manager.hint_taken(user, hint)

    def render_page(self, box, errors=[], success=[], info=[]):
        """ Wrapper to .render() to avoid duplicate code """
        user = self.get_current_user()
        self.render(
            "missions/box.html",
            box=box,
            user=user,
            team=user.team,
            errors=errors,
            success=success,
            info=info,
        )


class MissionsHandler(BaseHandler):

    """ Renders pages related to Missions/Flag submissions """

    @authenticated
    @game_started
    def get(self, *args, **kwargs):
        """ Render missions view """
        user = self.get_current_user()
        self.render("missions/view.html", team=user.team, errors=None, success=None)

    @authenticated
    @game_started
    def post(self, *args, **kwargs):
        """ Submit flags/buyout to levels """
        if self.get_current_user():
            uri = {"buyout": self.buyout}
            if len(args) and args[0] in uri:
                uri[str(args[0])]()
                return
        self.render("public/404.html")

    def buyout(self):
        """ Buyout and unlock a level """
        user = self.get_current_user()
        level = GameLevel.by_uuid(self.get_argument("uuid", ""))
        if level is not None:
            if level.buyout <= user.team.money:
                logging.info(
                    "%s (%s) paid buyout for %s"
                    % (user.handle, user.team.name, level.name)
                )
                user.team.game_levels.append(level)
                user.team.money -= level.buyout
                self.dbsession.add(user.team)
                self.dbsession.commit()
                self.event_manager.level_unlocked(user, level)
                self.redirect("/user/missions")
            else:
                self.render(
                    "missions/view.html",
                    team=user.team,
                    errors=["You do not have enough money to unlock this level"],
                    success=None,
                )
        else:
            self.render(
                "missions/view.html",
                team=user.team,
                errors=["Level does not exist"],
                success=None,
            )
