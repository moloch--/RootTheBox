# -*- coding: utf-8 -*-
"""
Created on Sep 20, 2012

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
"""

import logging

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketClosedError
from tornado.options import options
from libs.Singleton import Singleton
from builtins import object, str
from models import dbsession
from models.User import User
from models.Flag import Flag
from models.GameLevel import GameLevel
from models.PasteBin import PasteBin
from models.Notification import Notification, SUCCESS, INFO, WARNING, ERROR


@Singleton
class EventManager(object):

    """
    All event callbacks go here!
    This class holds refs to all open web sockets
    """

    public_connections = set()
    auth_connections = {}

    def __init__(self):
        self.io_loop = IOLoop.instance()

    # [ Connection Methods ] -----------------------------------------------
    def add_connection(self, connection):
        """Add a connection"""
        if connection.team_id is None:
            self.public_connections.add(connection)
        else:
            # Create team dictionary is none exists
            if connection.team_id not in self.auth_connections:
                self.auth_connections[connection.team_id] = {}
            # Create a set() of user connections, and/or add connection
            team_connections = self.auth_connections[connection.team_id]
            if connection.user_id not in team_connections:
                team_connections[connection.user_id] = set()
            team_connections[connection.user_id].add(connection)

    def remove_connection(self, connection):
        """Remove connection"""
        if connection.team_id is None or connection.user_id is None:
            self.public_connections.remove(connection)
        else:
            team_connections = self.auth_connections[connection.team_id]
            team_connections[connection.user_id].remove(connection)

    def deauth(self, user):
        """Send a deauth message to a user's client(s)"""
        if user.team is None:
            return
        connections = self.get_user_connections(user.team.id, user.id)
        for connection in connections:
            connection.close()

    def get_user_connections(self, team_id, user_id):
        """For an user object this method returns a set() of connections"""
        if team_id in self.auth_connections:
            if user_id in self.auth_connections[team_id]:
                return self.auth_connections[team_id][user_id]
        return set()

    def is_online(self, user):
        """
        Returns bool if the given user has an open notify socket
        """
        connections = self.get_user_connections(user.team.id, user.id)
        return False if connections is None or len(connections) == 0 else True

    @property
    def all_connections(self):
        """Iterate ALL THE THINGS!"""
        for team_id in self.auth_connections:
            for user_id in self.auth_connections[team_id]:
                for connection in self.auth_connections[team_id][user_id]:
                    yield connection
        for connection in self.public_connections:
            yield connection

    # [ Push Updates ] -----------------------------------------------------
    def push_broadcast(self):
        """Push to everyone"""
        for team_id in self.auth_connections:
            self.push_team(team_id)

    def push_team(self, team_id):
        if team_id in self.auth_connections:
            for user_id in self.auth_connections[team_id]:
                self.push_user(team_id, user_id)

    def push_user(self, team_id, user_id):
        """Push all unread notifications to open user websockets"""
        connections = self.get_user_connections(team_id, user_id)
        notifications = Notification.unread_by_user_id(user_id)
        logging.debug(
            "User #%s has %d unread notification(s)" % (user_id, len(notifications))
        )
        for notification in notifications:
            for connection in connections:
                self.safe_write_message(connection, notification.to_dict())
            notification.viewed = True
            dbsession.add(notification)
        dbsession.commit()

    def push_scoreboard(self):
        msg = {"update": ["scoreboard"]}
        for connection in self.all_connections:
            self.safe_write_message(connection, msg)

    def push_history(self, *args):
        msg = {"update": ["history"]}
        for connection in self.all_connections:
            self.safe_write_message(connection, msg)

    def safe_write_message(self, connection, msg):
        """
        Catches and handles possible exceptions that occur when sending
        messages over the websocket.
        """
        try:
            connection.write_message(msg)
        except WebSocketClosedError:
            self.io_loop.add_callback(self.remove_connection, connection)

    # [ Broadcast Events ] -------------------------------------------------
    def admin_score_update(self, team, message, value):
        """Callback for when admin point change is made"""
        if value < 0:
            icon = WARNING
        else:
            icon = SUCCESS
        Notification.create_team(
            team, "Admin Update", "%s (%s)" % (message, str(value)), icon
        )
        self.io_loop.add_callback(self.push_team, team.id)
        self.io_loop.add_callback(self.push_scoreboard)

    def push_score_update(self):
        self.io_loop.add_callback(self.push_scoreboard)

    def admin_message(self, message):
        """Callback for when admin point change is made"""
        Notification.create_broadcast(None, "Admin Message", message, INFO)
        self.io_loop.add_callback(self.push_broadcast)
        self.io_loop.add_callback(self.push_scoreboard)

    def flag_decayed(self, team, flag):
        """Callback for when a bot is added"""
        message = (
            "The value of challenge %s has decreased due to other team captures - score adjusted."
            % (flag.name,)
        )
        Notification.create_team(team, "Flag Value Decreased", message, INFO)
        self.io_loop.add_callback(self.push_team, team.id)

    def flag_captured(self, player, flag):
        """Callback for when a flag is captured"""
        if isinstance(player, User):
            team = player.team
        else:
            team = player
        if isinstance(player, User) and options.teams:
            message = '%s (%s) has completed "%s" in %s' % (
                player.handle,
                team.name,
                flag.name,
                flag.box.name,
            )
        else:
            message = '%s has completed "%s" in %s' % (
                team.name,
                flag.name,
                flag.box.name,
            )
        if len(GameLevel.all()) > 1:
            message = message + " (%s)" % (
                GameLevel.by_id(flag.box.game_level_id).name,
            )
        Notification.create_broadcast(team, "Flag Capture", message, SUCCESS)
        self.io_loop.add_callback(self.push_broadcast)
        self.io_loop.add_callback(self.push_scoreboard)

    def bot_added(self, user, count):
        """Callback for when a bot is added"""
        if options.teams:
            message = "%s (%s) added a new bot; total number of bots is now %d" % (
                user.handle,
                user.team.name,
                count,
            )
        else:
            message = "%s added a new bot; total number of bots is now %d" % (
                user.team.name,
                count,
            )
        Notification.create_broadcast(user.team, "Bot added", message, INFO)
        self.io_loop.add_callback(self.push_broadcast)
        self.io_loop.add_callback(self.push_scoreboard)

    def bot_scored(self, team, message=None):
        """Callback for when a bot scores"""
        if message is None:
            message = "%s botnet has scored" % team.name
        Notification.create_team(team, "Botnet Scored", message, SUCCESS)
        self.io_loop.add_callback(self.push_team, team.id)
        self.io_loop.add_callback(self.push_scoreboard)

    def hint_taken(self, user, hint):
        """Callback for when a hint is taken"""
        if options.teams:
            message = "%s has taken a hint for %s" % (user.handle, hint.box.name)
        else:
            message = "%s has taken a hint for %s" % (user.team.name, hint.box.name)
        if len(GameLevel.all()) > 1:
            message = message + " (%s)" % (
                GameLevel.by_id(hint.box.game_level_id).name,
            )
        Notification.create_team(user.team, "Hint Taken", message, INFO)
        self.io_loop.add_callback(self.push_team, user.team.id)
        self.io_loop.add_callback(self.push_scoreboard)

    def flag_penalty(self, user, flag):
        """Callback for when a flag is captured"""
        if options.teams:
            message = "%s was penalized on '%s' in %s" % (
                user.handle,
                flag.name,
                flag.box.name,
            )
        else:
            message = "%s was penalized on '%s' in %s" % (
                user.team.name,
                flag.name,
                flag.box.name,
            )
        if len(GameLevel.all()) > 1:
            message = message + " (%s)" % (
                GameLevel.by_id(flag.box.game_level_id).name,
            )
        Notification.create_team(user.team, "Flag Penalty", message, WARNING)
        self.io_loop.add_callback(self.push_team, user.team.id)
        self.io_loop.add_callback(self.push_scoreboard)

    def level_unlocked(self, user, level):
        """Callback for when a team unlocks a new level"""
        message = "%s unlocked %s." % (user.team.name, level.name)
        Notification.create_broadcast(user.team, "Level Unlocked", message, SUCCESS)
        self.io_loop.add_callback(self.push_broadcast)
        self.io_loop.add_callback(self.push_scoreboard)

    def item_purchased(self, user, item):
        """Callback when a team purchases an item"""
        message = "%s purchased %s from the black market" % (user.handle, item.name)
        Notification.create_team(user.team, "Upgrade Purchased", message, SUCCESS)
        self.io_loop.add_callback(self.push_team, user.team.id)
        self.io_loop.add_callback(self.push_scoreboard)

    def player_swated(self, user, target):
        if options.teams:
            message = "%s (%s) called the SWAT team on %s (%s)." % (
                user.handle,
                user.team.name,
                target.handle,
                target.team.name,
            )
        else:
            message = "%s called the SWAT team on %s." % (user.handle, target.handle)
        Notification.create_broadcast(user.team, "Player Arrested!", message, INFO)
        self.io_loop.add_callback(self.push_broadcast)
        self.io_loop.add_callback(self.push_scoreboard)

    # [ Team Events ] ------------------------------------------------------
    def user_joined_team(self, user):
        """Callback when a user joins a team"""
        if options.teams:
            message = "%s has joined the %s team" % (user.handle, user.team.name)
            Notification.create_team(user.team, "New Team Member", message, INFO)
        else:
            message = "%s has joined the game" % (user.handle,)
            Notification.create_team(user.team, "New Player", message, INFO)
        self.io_loop.add_callback(self.push_team, user.team.id)
        self.io_loop.add_callback(self.push_scoreboard)

    def team_file_shared(self, user, team, file_upload):
        """Callback when a team file share is created"""
        message = "%s has shared the file '%s'" % (user.handle, file_upload.file_name)
        Notification.create_team(team, "File Share", message, INFO)
        self.io_loop.add_callback(self.push_team, team.id)

    def team_paste_shared(self, user, team, paste_bin):
        """Callback when a pastebin is created"""
        message = "%s posted '%s' to the team paste bin" % (user.handle, paste_bin.name)
        Notification.create_team(team, "Text Share", message, INFO)
        self.io_loop.add_callback(self.push_team, team.id)

    # [ Misc Events ] ------------------------------------------------------
    def cracked_password(self, cracker, victim, password, value):
        """
        This is created when a user successfully cracks another
        players password.
        """
        user_msg = "Your password '%s' was cracked by %s" % (password, cracker.handle)
        Notification.create_user(victim, "Security Breach", user_msg, ERROR)
        message = "%s hacked %s's bank account and stole $%d" % (
            cracker.handle,
            victim.team.name,
            value,
        )
        Notification.create_broadcast(
            cracker.team, "Password Cracked", message, SUCCESS
        )
        self.io_loop.add_callback(self.push_broadcast)
        self.io_loop.add_callback(self.push_scoreboard)
