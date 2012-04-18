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

from models import User
from models import User, Action
from base64 import b64decode
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler
from libs.WebSocketManager import WebSocketManager
from libs.Notification import Notification

class CrackMeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
        self.session_manager = SessionManager.Instance()
        self.session = self.session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' '''
        user = User.by_user_name(self.session.data['user_name'])
        if user.team != None:
            self.render('crack_me/view.html', crack_me = user.team.crack_me)
        else:
            self.render('crack_me/view.html', crack_me = None)
             
    @authenticated
    def post(self, *args, **kwargs):
        ''' Check to see if the user correctly entered the crackme's token '''
        try:
            token = self.get_argument("token")
        except:
            self.render('crack_me/error.html', errors = "No token input")

        user = User.by_user_name(self.session.data['user_name'])
        if user != None:
            if(user.team.crack_me.token == token):
                level = user.team.crack_me.id
                user_action = Action(
                    classification = unicode("Cracked a Crack Me"),
                    description = unicode("%s successfully cracked the level %s" % (user.display_name, level)),
                    value = user.team.crack_me.value,
                    user_id = user.id
                )
                user.dirty = True
                self.notify(user, user.team.crack_me)
                user.team.solved_crack_me()
                user.actions.append(user_action)
                self.dbsession.add(user)
                self.dbsession.add(user.team)
                self.dbsession.flush()
                self.render('crack_me/success.html', level = level)
            else:
                self.render('crack_me/error.html', errors = "Invalid Token")
        else:
            self.redirect("/login")

    def notify(self, user, crack_me):
        ''' Send a notification to everyone that someone cracked a Crack Me '''
        title = "Crack Me Cracked!"
        message = unicode("%s successfully cracked the level %s Crack Me" % (user.display_name, crack_me.id))
        file_path = self.application.settings['avatar_dir']+'/'+user.avatar
        ws_manager = WebSocketManager.Instance()
        notify = Notification(title, message, file_location = file_path)
        ws_manager.send_all(notify)
 
    
class CrackMeDownloadHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        ''' Need to fix the Http header injection vuln '''
        session_manager = SessionManager.Instance()
        session = session_manager.get_session(self.get_secure_cookie('auth'), self.request.remote_ip)
        if session != None:
            user = User.by_user_name(session.data['user_name'])
            if user.team.crack_me != None:
                filePath = self.application.settings['crack_me_dir']+'/'+user.team.crack_me.uuid
                current = open(filePath, 'rb')
                data = current.read()
                current.close()
                self.set_header('Content-Type', user.team.crack_me.content)
                self.set_header('Content-Disposition', 'attachment; filename=%s' % user.team.crack_me.file_name)
                self.write(b64decode(data))
                self.write(data)
                self.finish()
            else:
                self.render('crack_me/complete.html')
        else:
            self.redirect("/login")
