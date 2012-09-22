# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

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


from tornado.web import RequestHandler
from models import Team, User, WallOfSheep
from libs.SecurityDecorators import authenticated
from libs.WebSocketManager import WebSocketManager
from libs.Notification import Notification
from libs.ScoreUpdate import ScoreUpdate
from libs.Session import SessionManager
from handlers.BaseHandlers import BaseHandler


class HashesHandler(BaseHandler):
    ''' Displays user password hashes '''

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders hashes page '''
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(
            self.get_secure_cookie('auth'), self.request.remote_ip)
        user = User.by_user_name(session.data['user_name'])
        self.render(
            "hashes/view.html", teams=Team.get_all(), current=user.team)

    @authenticated
    def post(self, *args, **kwargs):
        ''' Submit cracked hashes get checked '''
        # Get target display_name
        try:
            display_name = self.get_argument("display_name")
        except:
            self.render("hashes/error.html",
                        operation="Hash cracking", errors="No user name")
        # Get preimage
        try:
            preimage = self.get_argument("preimage")
        except:
            self.render("hashes/error.html",
                        errors="No password", operation="Hash cracking")
        user = User.by_user_name(self.session.data['user_name'])
        target = User.by_display_name(display_name)
        if target == None or user == None or target.has_permission("admin"):
            self.render("hashes/error.html", operation="Hash cracking",
                        errors="That user does not exist")
        elif target in user.team.members:
            self.render("hashes/error.html", operation="Hash cracking",
                        errors="You can't crack hashes from your own team")
        elif target.score <= 0:
            self.render("hashes/error.html", operation="Hash cracking",
                        errors="Target user must have a score greater than zero")
        elif target.validate_password(preimage):
            self.notify(user, target)
            value = self.steal_points(user, target)
            self.add_to_wall(user, target, preimage, value)
            self.render("hashes/success.html", user=user, target=target)
        else:
            self.render("hashes/error.html", operation="Hash cracking",
                        errors="Wrong password, try again")

    def steal_points(self, user, target):
        ''' Creates actions if password cracking was successful '''
        value = target.score
        user_action = Action(
            classification=unicode("Hash Cracking"),
            description=unicode("%s cracked %s's password" %
                                (user.display_name, target.display_name)),
            value=value,
            user_id=user.id
        )
        target_action = Action(
            classification=unicode("Hash Cracking"),
            description=unicode("%s's password was cracked by %s" %
                                (target.display_name, user.display_name)),
            value=(value * -1),
            user_id = target.id
        )
        target.dirty = True
        user.dirty = True
        user.actions.append(user_action)
        target.actions.append(target_action)
        self.dbsession.add(target)
        self.dbsession.add(user)
        self.dbsession.flush()
        return value

    def add_to_wall(self, user, target, preimage, value):
        ''' Creates an entry in the wall of sheep '''
        sheep = WallOfSheep(
            preimage=unicode(preimage),
            point_value=value,
            user_id=target.id,
            cracker_id=user.id
        )
        self.dbsession.add(sheep)
        self.dbsession.flush()

    def notify(self, user, target):
        ''' Sends a password cracked message via web sockets '''
        file_path = self.application.settings['avatar_dir'] + '/' + user.avatar
        ws_manager = WebSocketManager.Instance()
        message = "%s's password was cracked by %s" % (
            target.display_name, user.display_name)
        notify = Notification(
            "Password Cracked", message, file_location=file_path)
        team_message = "Your team has lost points due to %s's weak password" % target.display_name
        alt = Notification("%d Points Stolen" % target.score,
                           team_message, classification="warning")
        ws_manager.send_all(notify)
        ws_manager.send_team(user.team, alt)


class HashesAjaxHandler(RequestHandler):

    @authenticated
    def get(self, *args, **kwargs):
        ''' Renders a user details div, requested via AJAX '''
        try:
            display_name = self.get_argument("user_details")
        except:
            self.write("No Data")
        user = User.by_display_name(display_name)
        if user == None:
            self.write("No Data")
        else:
            self.render("hashes/user_details.html", user=user)


class WallOfSheepHandler(BaseHandler):

    @authenticated
    def get(self, *args, **kwargs):
        self.render("wall_of_sheep/view.html", wall=WallOfSheep.get_all())
