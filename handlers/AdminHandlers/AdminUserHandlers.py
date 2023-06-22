# -*- coding: utf-8 -*-
"""
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


Handlers for user-related tasks.
"""
# pylint: disable=unused-wildcard-import
# pylint: disable=no-member


import logging

from models.Team import Team
from models.Box import Box
from models.Flag import Flag
from models.EmailToken import EmailToken
from models.Corporation import Corporation
from models.User import User, ADMIN_PERMISSION
from models.Permission import Permission
from models.GameLevel import GameLevel
from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import *
from libs.ValidationError import ValidationError
from libs.EventManager import EventManager
from libs.Identicon import identicon
from libs.ConfigHelpers import save_config
from builtins import str
from tornado.options import options
from netaddr import IPAddress


class AdminManageUsersHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render("admin/view/users.html", errors=None)


class AdminEditTeamsHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        try:
            group = self.get_argument("team_uuid", "all")
            message = self.get_argument("message", "")
            value = int(self.get_argument("money", 0))
            if group == "all":
                teams = Team.all()
                for team in teams:
                    team.set_score("admin", value + team.money)
                    self.dbsession.add(team)
            else:
                team = Team.by_uuid(group)
                team.set_score("admin", value + team.money)
                self.dbsession.add(team)
            self.dbsession.commit()
            self.event_manager.admin_score_update(team, message, value)
            self.redirect("/admin/users")
        except ValidationError as error:
            self.render("admin/view/users.html", errors=[str(error)])


class AdminEditUsersHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {"user": self.edit_user, "team": self.edit_team}
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.redirect("/admin/users")

    def edit_team(self):
        """Edits the team object"""
        try:
            team = Team.by_uuid(self.get_argument("uuid", ""))
            if team is None:
                raise ValidationError("Team does not exist")
            team.name = self.get_argument("name", team.name)
            team.motto = self.get_argument("motto", team.motto)
            team.set_score("admin", self.get_argument("money", team.money))
            team.notes = self.get_argument("notes", "")
            if hasattr(self.request, "files") and "avatarfile" in self.request.files:
                team.avatar = self.request.files["avatarfile"][0]["body"]
            else:
                avatar = self.get_argument("avatar", team.avatar)
                if team.avatar != avatar and avatar != "":
                    # allow for default without setting
                    team._avatar = avatar
            self.dbsession.add(team)
            self.dbsession.commit()
            self.event_manager.push_score_update()
            self.redirect("/admin/users")
        except ValidationError as error:
            self.render("admin/view/users.html", errors=[str(error)])

    def edit_user(self):
        """Update user objects in the database"""
        try:
            user = User.by_uuid(self.get_argument("uuid", ""))
            if user is None:
                raise ValidationError("User does not exist")
            handle = self.get_argument("handle", "")
            if user.handle != handle:
                if User.by_handle(handle) is None:
                    logging.info("Updated user handle %s -> %s" % (user.handle, handle))
                    user.handle = handle
                else:
                    raise ValidationError("Handle is already in use")
            name = self.get_argument("name", "")
            email = self.get_argument("email", "")
            notes = self.get_argument("notes", "")
            expire = self.get_argument("expire", "")
            if user.name != name:
                logging.info("Updated user Name %s -> %s" % (user.name, name))
                user.name = name
            if user.email != email:
                logging.info("Updated user Email %s -> %s" % (user.email, email))
                user.email = email
            if user.notes != notes:
                logging.info("Updated user Notes %s -> %s" % (user.notes, notes))
                user.notes = notes
            if user.expire != expire:
                logging.info("Updated user Expire %s -> %s" % (user.expire, expire))
                user.expire = expire
            if options.banking:
                hash_algorithm = self.get_argument("hash_algorithm", "")
                if hash_algorithm != user.algorithm:
                    if hash_algorithm in user.algorithms:
                        if 0 < len(self.get_argument("bank_password", "")):
                            logging.info(
                                "Updated %s's hashing algorithm %s -> %s"
                                % (user.handle, user.algorithm, hash_algorithm)
                            )
                            user.algorithm = hash_algorithm
                        else:
                            raise ValidationError(
                                "You must provide a new bank password when updating the hashing algorithm"
                            )
                    else:
                        raise ValidationError("Not a valid hash algorithm")
                if len(self.get_argument("bank_password", "")):
                    user.bank_password = self.get_argument("bank_password", "")
            password = self.get_argument("password", "")
            if password and len(password) > 0:
                user.password = password
            if hasattr(self.request, "files") and "avatarfile" in self.request.files:
                user.avatar = self.request.files["avatarfile"][0]["body"]
            else:
                avatar = self.get_argument("avatar", user.avatar)
                # allow for default without setting
                user._avatar = avatar
            admin = self.get_argument("admin", "false")
            team = Team.by_uuid(self.get_argument("team_uuid", ""))
            if team is not None:
                if user not in team.members:
                    logging.info(
                        "Updated %s's team %s -> %s"
                        % (user.handle, user.team_id, team.name)
                    )
                    user.team_id = team.id
            elif options.teams and admin != "true":
                raise ValidationError("Please select a valid Team.")

            if admin == "true" and not user.is_admin():
                logging.info("Promoted user %s to Admin" % user.handle)
                permission = Permission()
                permission.name = ADMIN_PERMISSION
                permission.user_id = user.id
                user.team_id = None
                self.dbsession.add(permission)
            elif admin == "false" and user.is_admin():
                logging.info("Demoted user %s to Player" % user.handle)
                if user == self.get_current_user():
                    self.render(
                        "admin/view/users.html", errors=["You cannont demote yourself."]
                    )
                    return
                if team is None:
                    team = Team.by_name(user.handle)
                if team is None:
                    team = self.create_team(user)
                user.team_id = team.id
                permissions = Permission.by_user_id(user.id)
                for permission in permissions:
                    if permission.name == ADMIN_PERMISSION:
                        self.dbsession.delete(permission)

            self.dbsession.add(user)
            self.dbsession.commit()
            self.event_manager.push_score_update()
            self.redirect("/admin/users")
        except ValidationError as error:
            self.render("admin/view/users.html", errors=[str(error)])

    def create_team(self, user):
        team = Team()
        team.name = user.handle
        team.motto = ""
        team._avatar = identicon(team.name, 6)
        if self.config.banking:
            team.set_score("start", self.config.starting_team_money)
        else:
            team.set_score("start", 0)
        level_0 = GameLevel.by_number(0)
        if not level_0:
            level_0 = GameLevel.all()[0]
        team.game_levels.append(level_0)
        self.dbsession.add(team)
        self.dbsession.commit()
        self.event_manager.push_score_update()
        return team


class AdminDeleteUsersHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {"user": self.del_user, "team": self.del_team}
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.redirect("/admin/users")

    def del_user(self):
        """
        Delete user objects in the database, you cannot delete yourself.
        """
        user = User.by_uuid(self.get_argument("uuid", ""))
        if user is None:
            self.render("admin/view/users.html", errors=["User does not exist"])
        elif user == self.get_current_user():
            self.render("admin/view/users.html", errors=["You cannot delete yourself."])
        else:
            logging.info("Deleted User: '%s'" % str(user.handle))
            EventManager.instance().deauth(user)
            tokens = EmailToken.by_user_id(user.id, all=True)
            if tokens:
                for token in tokens:
                    self.dbsession.delete(token)
                self.dbsession.commit()
            self.dbsession.delete(user)
            self.dbsession.commit()
            self.event_manager.push_score_update()
            self.redirect("/admin/users")

    def del_team(self):
        """
        Delete team objects in the database.
        """
        team = Team.by_uuid(self.get_argument("uuid", ""))
        if team is not None:
            logging.info("Deleted Team: '%s'" % str(team.name))
            for user in team.members:
                if user == self.get_current_user():
                    self.render(
                        "admin/view/users.html",
                        errors=["Unable to delete user %s" % user.handle],
                    )
                    return
                EventManager.instance().deauth(user)
                tokens = EmailToken.by_user_id(user.id, all=True)
                if tokens:
                    for token in tokens:
                        self.dbsession.delete(token)
                    self.dbsession.commit()
            self.dbsession.delete(team)
            self.dbsession.commit()
            self.event_manager.push_score_update()
            self.redirect("/admin/users")
        else:
            self.render("admin/view/users.html", errors=["Team does not exist"])


class AdminBanHammerHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {"add": self.ban_add, "clear": self.ban_clear, "config": self.ban_config}
        if len(args) and args[0] in uri:
            uri[args[0]]()
        self.redirect("/user")

    def ban_config(self):
        """Configure the automatic ban settings"""
        if self.get_argument("automatic_ban", "") == "true":
            self.application.settings["automatic_ban"] = True
            self.config.automatic_ban = True
            try:
                threshold = abs(int(self.get_argument("threshold_size", "10")))
            except ValueError:
                threshold = 10
            logging.info("Automatic ban enabled, with threshold of %d" % threshold)
            self.application.settings["blacklist_threshold"] = threshold
            self.config.blacklist_threshold = threshold
        else:
            logging.info("Automatic ban disabled")
            self.application.settings["automatic_ban"] = False
            self.config.automatic_ban = False
        save_config()

    def ban_add(self):
        """Add an ip address to the banned list"""
        try:
            ip = self.get_argument("ip", "")
            if not IPAddress(ip).is_loopback():
                logging.info("Banned new ip: %s" % ip)
                self.application.settings["blacklisted_ips"].append(ip)
        except:
            pass  # Don't care about exceptions here

    def ban_clear(self):
        """Remove an ip from the banned list"""
        ip = self.get_argument("ip", "")
        if ip == "all":
            self.application.settings["failed_logins"] = {}
            self.application.settings["blacklisted_ips"] = []
        elif ip in self.application.settings["blacklisted_ips"]:
            logging.info("Removed ban on ip: %s" % ip)
            self.application.settings["blacklisted_ips"].remove(ip)
        if ip in self.application.settings["failed_logins"]:
            self.application.settings["failed_logins"][ip] = 0


class AdminLockHandler(BaseHandler):

    """Used to manually lock/unlocked accounts"""

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """Calls an lock based on URL"""
        uri = {
            "user": self.lock_user,
            "box": self.lock_box,
            "flag": self.lock_flag,
            "corp": self.lock_corp,
            "level": self.lock_level,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def lock_user(self):
        """Toggle account lock"""
        user = User.by_uuid(self.get_argument("uuid", ""))
        if user is not None:
            user.locked = False if user.locked else True
            self.dbsession.add(user)
            self.dbsession.commit()
            self.event_manager.push_score_update()
            self.redirect("/admin/users")
        else:
            self.render("public/404.html")

    def lock_corp(self):
        uuid = self.get_argument("uuid", "")
        corp = Corporation.by_uuid(uuid)
        if corp is not None:
            corp.locked = False if corp.locked else True
            self.dbsession.add(corp)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects#%s" % corp.uuid)
        else:
            self.render("public/404.html")

    def lock_level(self):
        uuid = self.get_argument("uuid", "")
        level = GameLevel.by_uuid(uuid)
        if level is not None:
            level.locked = False if level.locked else True
            self.dbsession.add(level)
            self.dbsession.commit()
            self.redirect("/admin/view/game_levels")
        else:
            self.render("public/404.html")

    def lock_box(self):
        uuid = self.get_argument("uuid", "")
        box = Box.by_uuid(uuid)
        if box is not None:
            if box.locked_corp():
                self.render(
                    "admin/view/game_objects.html",
                    success=None,
                    errors=["Box Locked by Corporation Lock"],
                )
            elif box.locked_level():
                self.render(
                    "admin/view/game_objects.html",
                    success=None,
                    errors=["Box Locked by Level Lock"],
                )
            else:
                box.locked = False if box.locked else True
                self.dbsession.add(box)
                self.dbsession.commit()
                self.redirect("/admin/view/game_objects#%s" % box.uuid)
        else:
            self.render("public/404.html")

    def lock_flag(self):
        uuid = self.get_argument("uuid", "")
        print(uuid)
        flag = Flag.by_uuid(uuid)
        if flag is not None:
            flag.locked = False if flag.locked else True
            self.dbsession.add(flag)
            self.dbsession.commit()
            self.redirect("/admin/view/game_objects#%s" % flag.uuid)
        else:
            self.render("public/404.html")


class AdminAjaxUserHandler(BaseHandler):
    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {"user": self.user_details, "team": self.team_details}
        if len(args) and args[0] in uri:
            uri[args[0]]()

    def team_details(self):
        # print(self.get_argument('uuid', ''))
        team = Team.by_uuid(self.get_argument("uuid", ""))
        if team is not None:
            self.write(team.to_dict())
        else:
            self.write({})

    def user_details(self):
        user = User.by_uuid(self.get_argument("uuid", ""))
        # print(user)
        if user is not None:
            self.write(user.to_dict())
        else:
            self.write({})
