# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2012

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


import logging

from models import dbsession, User, Box
from libs.Notifier import Notifier
from tornado.web import RequestHandler


class ReporterRegistrationHandler(RequestHandler):

    def get(self, *args, **kwargs):
        ''' Registers a reporting service on a remote box '''
        box = Box.by_ip_address(self.request.remote_ip)
        if box != None:
            try:
                handle = self.get_argument("handle")
                user = User.by_handle(handle)
                if user != None:
                    if not box in user.team.boxes:
                        user.team.boxes.append(box)
                        dbsession.add(team)
                        dbsession.flush()
                    self.write(unicode(user.team.listen_port))
                else:
                    self.write("Invalid handle")
            except:
                self.write("Missing parameter")
        else:
            self.write("Invalid ip address")
        self.finish()

    def notify(self, user, box):
        ''' Sends notification of box ownage '''
        title = "Pwnage Report"
        message = "%s added %s to their botnet." % (user.team.name, box.name)
        icon = '/avatars/' + user.avatar
        Notifier.broadcast_custom(title, message, icon)
