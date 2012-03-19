'''
Created on Mar 13, 2012

@author: moloch
'''

from models import User
from models import User, Action
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler #@UnresolvedImport
from libs.WebSocketManager import WebSocketManager
from libs.Notification import Notification

class CrackMeHandler(RequestHandler):
    
    def initialize(self, dbsession):
        self.dbsession = dbsession
    
    @authenticated
    def get(self, *args, **kwargs):
        session = sessions[self.get_secure_cookie('auth')]
        user = User.by_user_name(session.data['user_name'])
        if user.team != None:
            self.render('crack_me/view.html', crack_me = user.team.crack_me)
        else:
            self.render('crack_me/view.html', crack_me = None)
             
    @authenticated
    def post(self, *args, **kwargs):
        ''' Check to see if the user correctly entered the crackme's token '''
        try:
            crack_me = self.get_argument("crack_me")
            crack_me = int(crack_me)
            token = self.get_argument("token")
        except:
            self.render('crack_me/error.html', errors="Enter a Token!")
        
        session = sessions[self.get_secure_cookie('auth')]
        user = User.by_user_name(session.data['user_name'])
        #If they are entering towards the correct crackme
        if(user.team.crack_me.id == crack_me):
            #If they entered the token correctly
            if(user.team.crack_me.token == token):
                user_action = Action(
                    classification = unicode("CrackMe Beaten"),
                    description = unicode("%s successfully cracked the level %s CrackMe" % (user.display_name, user.team.crack_me.id)),
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
                self.redirect("/crackmes")
            else:
                self.render('crack_me/error.html', errors="Invalid Token!")
        else:
            self.render('crack_me/error.html', errors="You're not on that CrackMe yet!")

    def notify(self, user, crack_me):
        ''' Send a notification to everyone that someone cracked a CrackMe '''
        title = "CrackMe Broken!"
        message = unicode("%s successfully cracked the level %s CrackMe" % (user.display_name, crack_me.id))
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
        session = self.session_manager.get_session([self.get_secure_cookie('auth'), self.request.remote_ip])
        if session != None:
            user = User.by_user_name(session.data['user_name'])
            if user.team.crack_me != None:
                filePath = self.application.settings['crack_me_dir']+'/'+user.team.crack_me.uuid
                current = open(filePath, 'rb')
                data = current.read()
                current.close()
                self.set_header("Content-Type", crack_me.content)
                self.write(data)
                self.finish()
            else:
                self.render('crack_me/complete.html')
