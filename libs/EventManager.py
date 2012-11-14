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
from libs.Scoreboard import ScoreboardManager
from models import User, Flag, FileUpload


@Singleton
class EventManager(object):
    '''
    All event callbacks go here!
    '''

    def __init__(self):
        self.notifier = Notifier()
        self.scoreboard = ScoreboardManager.Instance()

    def joined_team(self, user):
        message = "%s has joined your team." % user.handle
        self.notifier.team_success(user.team, "New Team Member", message)

    def flag_capture(self, user, flag):
        ''' Callback for when a flag is captured '''
        self.scoreboard.refresh()
        self.notifier.broadcast_success("Flag Capture", "%s has captured '%s'." % (user.team.name, flag.name,))

    def team_file_share(self, user, file_upload):
        message = "%s has shared a file called '%s'" % (user.handle, file_upload.file_name,)
        self.notifier.team_success(user.team, "File Share", message)