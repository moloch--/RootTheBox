'''
Created on Mar 13, 2012

@author: moloch

 Copyright [2012] [Redacted Labs]

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

from models import User, Box
from libs.Notification import Notification
from libs.WebSocketManager import WebSocketManager
from tornado.web import RequestHandler, asynchronous  # @UnresolvedImport


class ReporterRegistrationHandler(RequestHandler):

    def initialize(self, dbsession):
        ''' Sets up database connection '''
        self.dbsession = dbsession

    @asynchronous
    def get(self, *args, **kwargs):
        ''' Registers a reporting service on a remote box '''
        box = Box.by_ip_address(self.request.remote_ip)
        if box != None:
            try:
                display_name = self.get_argument("handle")
                user = User.by_display_name(display_name)
                if user != None and not user.team.is_controlling(box):
                    user.give_control(box)
                    self.dbsession.add(user)
                    self.dbsession.flush()
                    self.notify(user, box)
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
        title = "Box Owned!"
        message = "%s owned %s" % (user.display_name, box.box_name)
        notify = Notification(title, message, file_location=self.
                              application.settings['avatar_dir'] + '/' + user.avatar)
        ws_manager = WebSocketManager.Instance()
        ws_manager.send_all(notify)
