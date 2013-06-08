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
        self.notify_connections = {}
        self.scoreboard_connections = []
        self.history_connections = []
        self.scoreboard = Scoreboard()

    @property
    def users_online(self):
        ''' Number of currently open notify sockets '''
        sumation = 0
        for team_id in self.notify_connections:
            sumation += len(self.notify_connections[team_id])
        return sumation

    def is_online(self, user):
        ''' 
        Returns bool if the given user has an open notify socket
        '''
        if user.team.id in self.notify_connections:
            if user.id in self.notify_connections[user.team.id]:
                return 0 < len(self.notify_connections[user.team.id][user.id])
        return False

    # [ Connection Methods ] -----------------------------------------------
    def add_connection(self, wsocket):
        ''' Add a connection '''
        if not wsocket.team_id in self.notify_connections:
            self.notify_connections[wsocket.team_id] = {}
        if wsocket.user_id in self.notify_connections[wsocket.team_id]:
            self.notify_connections[wsocket.team_id][wsocket.user_id].append(wsocket)
        else:
            self.notify_connections[wsocket.team_id][wsocket.user_id] = [wsocket]

    def remove_connection(self, wsocket):
        ''' Remove connection '''
        self.notify_connections[wsocket.team_id][wsocket.user_id].remove(wsocket)
        if len(self.notify_connections[wsocket.team_id][wsocket.user_id]) == 0:
            del self.notify_connections[wsocket.team_id][wsocket.user_id]

    def deauth(self, user):
        if user.team.id in self.notify_connections:
            if user.id in self.notify_connections[user.team.id]:
                wsocks = self.notify_connections[user.team.id][user.id]
                for wsock in wsocks:
                    wsock.write_message({
                        'warn': "You have been deauthenticated"
                    })
                    wsock.close()

    # [ Push Updates ] -----------------------------------------------------
    def refresh_scoreboard(self):
        ''' Push to everyone '''
        update = self.scoreboard.now()
        for wsocket in self.scoreboard_connections:
            wsocket.write_message(update)

    def push_history(self, snapshot):
        ''' Push latest snapshot to everyone '''
        for wsocket in self.history_connections:
            wsocket.write_message({'update': snapshot})

    def push_broadcast_notification(self, event_uuid):
        ''' Push to everyone '''
        json = Notification.by_event_uuid(event_uuid).to_json()
        for team_id in self.notify_connections:
            for user_id in self.notify_connections[team_id]:
                for wsocket in self.notify_connections[team_id][user_id]:
                    wsocket.write_message(json)
                    # Only mark delivered for non-public users
                    if wsocket.user_id != '$public_user':
                        Notification.delivered(user_id, event_uuid)

    def push_team_notification(self, event_uuid, team_id):
        ''' Push to one team '''
        if team_id in self.notify_connections:
            json = Notification.by_event_uuid(event_uuid).to_json()
            for user_id in self.notify_connections[team_id]:
                for wsocket in self.notify_connections[team_id][user_id]:
                    wsocket.write_message(json)
                    Notification.delivered(wsocket.user_id, event_uuid)

    def push_user_notification(self, event_uuid, team_id, user_id):
        ''' Push to one user '''
        if team_id in self.notify_connections and user_id in self.notify_connections[team_id]:
            json = Notification.by_event_uuid(event_uuid).to_json()
            for wsocket in self.notify_connections[team_id][user_id]:
                wsocket.write_message(json)
                Notification.delivered(wsocket.user_id, event_uuid)

    # [ Broadcast Events ] -------------------------------------------------
    def create_flag_capture_event(self, user, flag):
        ''' Callback for when a flag is captured '''
        self.refresh_scoreboard()
        evt_id = Notifier.broadcast_success("Flag Capture", 
            "%s has captured '%s'." % (user.team.name, flag.name,)
        )
        return (self.push_broadcast_notification, {'event_uuid': evt_id})

    def create_unlocked_level_event(self, user, level):
        ''' Callback for when a team unlocks a new level '''
        self.refresh_scoreboard()
        message = "%s unlocked level #%d." % (user.team.name, level.number,)
        evt_id = Notifier.broadcast_success("Level Unlocked", message)
        return (self.push_broadcast_notification, {'event_uuid': evt_id})

    def create_purchased_item_event(self, user, item):
        ''' Callback when a team purchases an item '''
        self.refresh_scoreboard()
        message = "%s purchased %s from the black market." % (
            user.handle, item.name,
        )
        evt_id = Notifier.team_success(user.team, "Upgrade Purchased", message)
        self.push_broadcast_notification(evt_id)
        message2 = "%s unlocked %s." % (user.team.name, item.name,)
        evt_id2 = Notifier.broadcast_warning("Team Upgrade", message2)
        return (self.push_broadcast_notification, {'event_uuid': evt_id2})

    def create_swat_player_event(self, user, target):
        message("%s called the SWAT team on %s." % (user.handle, target.handle,))
        evt_id = Notifier.broadcast_warning("Player Arrested!", message)
        return (self.push_broadcast_notification, {'event_uuid': evt_id})

    # [ Team Events ] ------------------------------------------------------
    def create_joined_team_event(self, user):
        ''' Callback when a user joins a team'''
        message = "%s has joined your team." % user.handle
        evt_id = Notifier.team_success(user.team, "New Team Member", message)
        return (self.push_team_notification, {
            'event_uuid': evt_id, 
            'team_id': user.team.id
        })

    def create_team_file_share_event(self, user, file_upload):
        ''' Callback when a team file share is created '''
        message = "%s has shared a file called '%s'" % (
            user.handle, file_upload.file_name,
        )
        evt_id = Notifier.team_success(user.team, "File Share", message)
        return (self.push_team_notification, {
            'event_uuid':evt_id, 
            'team_id':user.team.id
        })

    def create_paste_bin_event(self, user, paste):
        ''' Callback when a pastebin is created '''
        message = "%s posted to the team paste-bin" % user.handle
        evt_id = Notifier.team_success(user.team, "Text Share", message)
        return (self.push_team_notification, {
            'event_uuid': evt_id, 
            'team_id': user.team.id
        })

    # [ Misc Events ] ------------------------------------------------------
    def create_cracked_password_events(self, cracker, victim, password, value):
        user_msg = "Your password '%s' was cracked by %s." % (
            password, cracker.handle,
        )
        evt_id = Notifier.user_warning(victim, "Security Breach", user_msg)
        event1 = (self.push_user_notification, {
            'event_uuid': evt_id, 
            'team_id': victim.team.id, 
            'user_id': victim.id
        })
        message = "%s hacked %s's bank account and stole $%d" % (
            cracker.handle, victim.team.name, value,
        )
        evt_id = Notifier.broadcast_custom("Password Cracked",
            message, cracker.avatar
        )
        event2 = (self.push_broadcast_notification, {'event_uuid':evt_id})
        return event1, event2
