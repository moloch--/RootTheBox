# -*- coding: utf-8 -*-
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

from models.User import User
from models.Action import Action
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler  # @UnresolvedImport
from libs.SEManager import SEManager
from libs.Session import SessionManager
from libs.WebSocketManager import WebSocketManager
from libs.Notification import Notification


class SocialHomeHandler(RequestHandler):

    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.session_manager = SessionManager.Instance()
        self.session = self.session_manager.get_session(
            self.get_secure_cookie('auth'), self.request.remote_ip)

    @authenticated
    def get(self, *args, **kwargs):
        se_manager = SEManager.Instance()
        self.render("se/view.html", current_se=se_manager.get_current())

    @authenticated
    def post(self, *args, **kwargs):
        try:
            token = self.get_argument("token")
        except:
            self.render('se/submit.html', message="Please enter a token!")

        user = User.by_user_name(self.session.data['user_name'])
        se_manager = SEManager.Instance()
        challenge = se_manager.active_challenge
        if token == se_manager.active_challenge.token:
            se_manager.active_challenge.team_id = user.team.id
            action = Action(
                classification=unicode(
                    "Defeated a Social Engineering Challenge"),
                description=unicode("%s successfully defeated the level %s Social Engineering Challenge" % (user.display_name, se_manager.active_challenge.level)),
                value=challenge.value,
                user_id=user.id)
            se_manager.update_challenge()
            self.notify(user, challenge)
            self.dbsession.add(challenge)
            self.dbsession.add(user)
            self.dbsession.add(action)
            self.dbsession.flush()
            self.render('se/submit.html', message="You have successfully completed a Social Engineering Round!")

    def notify(self, user, se):
        '''Send a notification to everyone that a round of the social engineering challenge has updated '''
        title = "Social Engineering Round Compelete!"
        message = unicode("%s successfully defeated the level %s Social Engineering Challenge" % (user.display_name, se.level))
        file_path = self.application.settings['avatar_dir'] + '/' + user.avatar
        ws_manager = WebSocketManager.Instance()
        notify = Notification(title, message, file_location=file_path)
        ws_manager.send_all(notify)
