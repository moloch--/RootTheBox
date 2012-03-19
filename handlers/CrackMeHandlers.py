'''
Created on Mar 13, 2012

@author: moloch
'''

from models import User
from libs.Session import SessionManager
from libs.SecurityDecorators import authenticated
from tornado.web import RequestHandler #@UnresolvedImport

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