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
from models.User import User, ADMIN_PERMISSION
from models.Permission import Permission
from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import *
from libs.ValidationError import ValidationError
from libs.EventManager import EventManager
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
                    team.money += value
                    self.dbsession.add(team)
                    self.event_manager.admin_score_update(team, message, value)
            else:
                team = Team.by_uuid(group)
                team.money += value
                self.dbsession.add(team)
                self.event_manager.admin_score_update(team, message, value)
            self.dbsession.commit()
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
        """ Edits the team object """
        try:
            team = Team.by_uuid(self.get_argument("uuid", ""))
            if team is None:
                raise ValidationError("Team does not exist")
            team.name = self.get_argument("name", team.name)
            team.motto = self.get_argument("motto", team.motto)
            team.money = self.get_argument("money", team.money)
            if hasattr(self.request, "files") and "avatarfile" in self.request.files:
                team.avatar = self.request.files["avatarfile"][0]["body"]
            else:
                avatar = self.get_argument("avatar", team.avatar)
                if team.avatar != avatar and avatar != "":
                    # allow for default without setting
                    team._avatar = avatar
            self.dbsession.add(team)
            self.dbsession.commit()
            self.redirect("/admin/users")
        except ValidationError as error:
            self.render("admin/view/users.html", errors=[str(error)])

    def edit_user(self):
        """ Update user objects in the database """
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
            if user.name != name:
                logging.info("Updated user Name %s -> %s" % (user.name, name))
                user.name = name
            if user.email != email:
                logging.info("Updated user Email %s -> %s" % (user.email, email))
                user.email = email
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
            team = Team.by_uuid(self.get_argument("team_uuid", ""))
            if team is not None:
                if user not in team.members:
                    logging.info(
                        "Updated %s's team %s -> %s"
                        % (user.handle, user.team_id, team.name)
                    )
                    user.team_id = team.id
            elif options.teams:
                raise ValidationError("Team does not exist in database")
            self.dbsession.add(user)

            admin = self.get_argument("admin", "false")
            if admin == "true" and not user.is_admin():
                permission = Permission()
                permission.name = ADMIN_PERMISSION
                permission.user_id = user.id
                self.dbsession.add(permission)
            elif admin == "false" and user.is_admin():
                permissions = Permission.by_user_id(user.id)
                for permission in permissions:
                    if permission.name == ADMIN_PERMISSION:
                        self.dbsession.delete(permission)

            self.dbsession.commit()
            self.redirect("/admin/users")
        except ValidationError as error:
            self.render("admin/view/users.html", errors=[str(error)])


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
        if user is not None and user != self.get_current_user():
            logging.info("Deleted User: '%s'" % str(user.handle))
            self.dbsession.delete(user)
            self.dbsession.commit()
            self.redirect("/admin/users")
        else:
            self.render("admin/view/users.html", errors=["User does not exist"])

    def del_team(self):
        """
        Delete team objects in the database.
        """
        team = Team.by_uuid(self.get_argument("uuid", ""))
        for user in team.members:
            if user == self.get_current_user():
                self.render(
                    "admin/view/users.html",
                    errors=["Unable to delete user %s" % user.handle],
                )
                return
            EventManager.instance().deauth(user)
        if team is not None:
            logging.info("Deleted Team: '%s'" % str(team.name))
            self.dbsession.delete(team)
            self.dbsession.commit()
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
        """ Configure the automatic ban settings """
        if self.get_argument("automatic_ban", "") == "true":
            self.application.settings["automatic_ban"] = True
            try:
                threshold = abs(int(self.get_argument("threshold_size", "10")))
            except ValueError:
                threshold = 10
            logging.info("Automatic ban enabled, with threshold of %d" % threshold)
            self.application.settings["blacklist_threshold"] = threshold
        else:
            logging.info("Automatic ban disabled")
            self.application.settings["automatic_ban"] = False

    def ban_add(self):
        """ Add an ip address to the banned list """
        try:
            ip = self.get_argument("ip", "")
            if not IPAddress(ip).is_loopback():
                logging.info("Banned new ip: %s" % ip)
                self.application.settings["blacklisted_ips"].append(ip)
        except:
            pass  # Don't care about exceptions here

    def ban_clear(self):
        """ Remove an ip from the banned list """
        ip = self.get_argument("ip", "")
        if ip in self.application.settings["blacklisted_ips"]:
            logging.info("Removed ban on ip: %s" % ip)
            self.application.settings["blacklisted_ips"].remove(ip)
        self.application.settings["failed_logins"][ip] = 0


class AdminLockHandler(BaseHandler):

    """ Used to manually lock/unlocked accounts """

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        """ Toggle account lock """
        user = User.by_uuid(self.get_argument("uuid", ""))
        if user is not None:
            user.locked = False if user.locked else True
            self.dbsession.add(user)
            self.dbsession.commit()
        self.redirect("/admin/users")


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
