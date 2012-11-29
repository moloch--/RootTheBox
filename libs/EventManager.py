# -*- coding: utf-8 -*-
'''
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
'''


from libs.Notifier import Notifier
from libs.Singleton import Singleton
from libs.Scoreboard import Scoreboard
from libs.SecurityDecorators import debug
from models import Notification


@Singleton
class EventManager(object):
    '''
    All event callbacks go here!
    This class holds refs to all open web sockets
    '''

    def __init__(self):
        self.botnets = {}
        self.notify_connections = {}
        self.scoreboard_connections = []
        self.scoreboard = Scoreboard()

    @debug
    def add_connection(self, wsocket):
        ''' Add a connection '''
        if not wsocket.team_id in self.notify_connections:
            self.notify_connections[wsocket.team_id] = {}
        if wsocket.user_id in self.notify_connections[wsocket.team_id]:
            self.notify_connections[wsocket.team_id][wsocket.user_id].append(wsocket)
        else:
            self.notify_connections[wsocket.team_id][wsocket.user_id] = [wsocket]

    @debug
    def remove_connection(self, wsocket):
        ''' Remove connection '''
        self.notify_connections[wsocket.team_id][wsocket.user_id].remove(wsocket)
        if len(self.notify_connections[wsocket.team_id][wsocket.user_id]) == 0:
            del self.notify_connections[wsocket.team_id][wsocket.user_id]

    @debug
    def add_bot(self, bot_socket):
        ''' Add a bot to a team's botnet '''
        if not bot_socket.team.id in self.botnets:
            self.botnets[bot_socket.team.id] = {}
        if bot_socket.box.id in self.botnets[bot_socket.team.id]:
            self.botnets[bot_socket.team.id][bot_socket.box.id].close()
            del self.botnets[bot_socket.team.id][bot_socket.box.id]
        self.botnets[bot_socket.team.id][bot_socket.box.id] = bot_socket

    @debug
    def remove_bot(self, bot_socket):
        ''' Remove ref to bot connection '''
        del self.botnets[bot_socket.team.id][bot_socket.box.id]

    @debug
    def bot_count(self, team):
        ''' Get number of current bots owned by a given team '''
        if team.id in self.botnets:
            return len(self.botnets[team.id].keys())
        else:
            return 0

    # [ Push Updates ] -----------------------------------------------------

    @debug
    def refresh_scorboard(self):
        ''' Push to everyone '''
        update = self.scoreboard.now()
        for wsocket in self.scoreboard_connections:
            wsocket.write_message(update)

    @debug
    def push_broadcast_notification(self, event_uuid):
        ''' Push to everyone '''
        json = Notification.by_event_uuid(event_uuid).to_json()
        for team_id in self.notify_connections.keys():
            for user_id in self.notify_connections[team_id].keys():
                for wsocket in self.notify_connections[team_id][user_id]:
                    wsocket.write_message(json)
                    if wsocket.user_id != 'public_user':
                        Notification.delivered(user_id, event_uuid)

    @debug
    def push_team_notification(self, event_uuid, team_id):
        ''' Push to one team '''
        json = Notification.by_event_uuid(event_uuid).to_json()
        if team_id in self.notify_connections:
            for user_id in self.notify_connections[team_id].keys():
                for wsocket in self.notify_connections[team_id][user_id]:
                    wsocket.write_message(json)
                    Notification.delivered(wsocket.user_id, event_uuid)

    @debug
    def push_user_notification(self, event_uuid, team_id, user_id):
        ''' Push to one user '''
        json = Notification.by_event_uuid(event_uuid).to_json()
        if team_id in self.notify_connections and user_id in self.notify_connections[team_id]:
            for wsocket in self.notify_connections[team_id][user_id]:
                wsocket.write_message(json)
                Notification.delivered(wsocket.user_id, event_uuid)

    # [ Broadcast Events ] -------------------------------------------------

    @debug
    def flag_capture(self, user, flag):
        ''' Callback for when a flag is captured '''
        self.refresh_scorboard()
        evt_id = Notifier.broadcast_success(
            "Flag Capture", "%s has captured '%s'." % (user.team.name, flag.name,)
        )
        self.push_broadcast_notification(evt_id)

    @debug
    def unlocked_level(self, user, level):
        ''' Callback for when a team unlocks a new level '''
        self.refresh_scorboard()
        message = "%s unlocked level #%d" % (user.team.name, level.number)
        evt_id = Notifier.broadcast_success("Level Unlocked", message)
        self.push_broadcast_notification(evt_id)

    @debug
    def purchased_item(self, user, item):
        ''' Callback when a team purchases an item '''
        self.refresh_scorboard()
        message = "%s purchased %s from the black market." % (user.handle, item.name)
        evt_id = Notifier.team_success(user.team, "Upgrade Purchased", message)
        self.push_broadcast_notification(evt_id)
        message2 = "%s unlocked %s." % (user.team.name, item.name)
        evt_id2 = Notifier.broadcast_warning("Competitor Upgrade", message2)
        self.push_broadcast_notification(evt_id2)

    # [ Team Events ] ------------------------------------------------------

    @debug
    def joined_team(self, user):
        ''' Callback when a user joins a team'''
        message = "%s has joined your team." % user.handle
        evt_id = Notifier.team_success(user.team, "New Team Member", message)
        self.push_team_notification(evt_id, user.team.id)

    @debug
    def team_file_share(self, user, file_upload):
        ''' Callback when a team file share is created '''
        message = "%s has shared a file called '%s'" % (user.handle, file_upload.file_name,)
        evt_id = Notifier.team_success(user.team, "File Share", message)
        self.push_team_notification(evt_id)

    @debug
    def paste_bin(self, user, paste):
        ''' Callback when a pastebin is created '''
        message = "%s posted to the team paste-bin" % user.handle
        evt_id = Notifier.team_success(user.team, "Text Share", message)
        self.push_team_notification(evt_id)

    @debug
    def new_bot(self, bot):
        message = "New bot connected to botnet from %s " % (bot.box.name,)
        evt_id = Notifier.team_success(bot.team, "Botnet", message)
        self.push_team_notification(evt_id)

    @debug
    def lost_bot(self, bot):
        message = "Lost communication with bot on %s" % (bot.box.name,)
        evt_id = Notifier.team_warning(bot.team, "Botnet", message)
        self.push_team_notification(evt_id)

    # [ User Events ] ------------------------------------------------------

    @debug
    def password_cracked(self, sheep):
        pass
