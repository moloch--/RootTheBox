# -*- coding: utf-8 -*-
"""
Created on Jun 24, 2019

@author: eljeffe

    Copyright 2019 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import logging

from builtins import object
from rocketchat_API.rocketchat import RocketChat
from tornado.options import options


class ChatManager(object):
    def __init__(self, username="", password="", server_url="", ssl_verify=False):
        self.rocket = RocketChat(
            user=username,
            password=password,
            server_url=server_url,
            ssl_verify=ssl_verify,
        )

    def create_user(self, user, password):
        # Create the user's account on RocketChat
        if not self.rocket:
            return
        account = self.rocket.users_create(
            user.email, user.name, password, user.handle
        ).json()
        self.create_team(user.team, account)

    def create_team(self, team, account):
        # Create a private team group
        if options.teams:
            group = self.has_group(team)
            if not group:
                groups = self.rocket.groups_create(team.name).json()
                group = groups["group"]
            self.rocket.groups_invite(group["_id"], account["user"]["_id"])

    def has_group(self, team):
        if not team:
            return False
        privaterooms = self.rocket.groups_list().json()
        if "groups" in privaterooms:
            for group in privaterooms["groups"]:
                if group["name"] == team.name:
                    return group
        return False
